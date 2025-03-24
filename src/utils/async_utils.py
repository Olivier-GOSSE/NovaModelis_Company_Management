"""
Utilitaires pour les opérations asynchrones dans l'application.
"""
import asyncio
import threading
import functools
import logging
from typing import Callable, Any, Coroutine, TypeVar, Optional, List, Dict, Union
from concurrent.futures import ThreadPoolExecutor

# Type générique pour les résultats de fonctions
T = TypeVar('T')

# Exécuteur de threads global pour les tâches asynchrones
_thread_executor = ThreadPoolExecutor(max_workers=10)

# Boucle d'événements asyncio pour le thread principal
_main_event_loop = None

def init_async_support():
    """
    Initialiser le support asynchrone pour l'application.
    Cette fonction doit être appelée au démarrage de l'application.
    """
    global _main_event_loop
    
    # Créer une nouvelle boucle d'événements
    _main_event_loop = asyncio.new_event_loop()
    
    # Définir la boucle d'événements comme boucle par défaut pour le thread principal
    asyncio.set_event_loop(_main_event_loop)
    
    logging.info("Support asynchrone initialisé")

def run_async(coroutine: Coroutine) -> Any:
    """
    Exécuter une coroutine de manière synchrone.
    
    Args:
        coroutine: La coroutine à exécuter.
        
    Returns:
        Le résultat de la coroutine.
    """
    global _main_event_loop
    
    if _main_event_loop is None:
        init_async_support()
    
    # Exécuter la coroutine dans la boucle d'événements
    return asyncio.run_coroutine_threadsafe(coroutine, _main_event_loop).result()

def async_to_sync(func: Callable[..., Coroutine]) -> Callable[..., Any]:
    """
    Décorateur pour convertir une fonction asynchrone en fonction synchrone.
    
    Args:
        func: La fonction asynchrone à convertir.
        
    Returns:
        Une fonction synchrone qui exécute la fonction asynchrone.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return run_async(func(*args, **kwargs))
    
    return wrapper

def run_in_executor(func: Callable[..., T]) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    Décorateur pour exécuter une fonction bloquante dans un pool de threads.
    
    Args:
        func: La fonction bloquante à exécuter.
        
    Returns:
        Une coroutine qui exécute la fonction dans un pool de threads.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _thread_executor,
            functools.partial(func, *args, **kwargs)
        )
    
    return wrapper

class AsyncTask:
    """
    Classe pour gérer une tâche asynchrone avec des callbacks.
    """
    def __init__(self, coroutine: Coroutine, on_success: Optional[Callable[[Any], None]] = None,
                 on_error: Optional[Callable[[Exception], None]] = None):
        """
        Initialiser une tâche asynchrone.
        
        Args:
            coroutine: La coroutine à exécuter.
            on_success: Callback appelé en cas de succès avec le résultat.
            on_error: Callback appelé en cas d'erreur avec l'exception.
        """
        self.coroutine = coroutine
        self.on_success = on_success
        self.on_error = on_error
        self.task = None
    
    def start(self):
        """
        Démarrer la tâche asynchrone.
        """
        global _main_event_loop
        
        if _main_event_loop is None:
            init_async_support()
        
        # Créer et démarrer la tâche
        self.task = asyncio.run_coroutine_threadsafe(self._run(), _main_event_loop)
    
    async def _run(self):
        """
        Exécuter la coroutine et appeler les callbacks appropriés.
        """
        try:
            result = await self.coroutine
            if self.on_success:
                self.on_success(result)
            return result
        except Exception as e:
            logging.error(f"Erreur dans la tâche asynchrone: {str(e)}")
            if self.on_error:
                self.on_error(e)
            raise
    
    def cancel(self):
        """
        Annuler la tâche asynchrone si elle est en cours d'exécution.
        """
        if self.task and not self.task.done():
            self.task.cancel()

class AsyncQueue:
    """
    File d'attente asynchrone pour traiter des tâches en arrière-plan.
    """
    def __init__(self, max_workers: int = 5):
        """
        Initialiser la file d'attente asynchrone.
        
        Args:
            max_workers: Nombre maximum de travailleurs simultanés.
        """
        self.queue = asyncio.Queue()
        self.max_workers = max_workers
        self.workers = []
        self.running = False
    
    async def worker(self):
        """
        Travailleur qui traite les tâches de la file d'attente.
        """
        while self.running:
            try:
                # Récupérer une tâche de la file d'attente
                task, args, kwargs, future = await self.queue.get()
                
                try:
                    # Exécuter la tâche
                    result = await task(*args, **kwargs)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
                finally:
                    # Marquer la tâche comme terminée
                    self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Erreur dans le travailleur de la file d'attente: {str(e)}")
    
    def start(self):
        """
        Démarrer la file d'attente.
        """
        global _main_event_loop
        
        if _main_event_loop is None:
            init_async_support()
        
        self.running = True
        
        # Créer les travailleurs
        for _ in range(self.max_workers):
            worker_task = asyncio.run_coroutine_threadsafe(self.worker(), _main_event_loop)
            self.workers.append(worker_task)
    
    def stop(self):
        """
        Arrêter la file d'attente.
        """
        self.running = False
        
        # Annuler tous les travailleurs
        for worker in self.workers:
            worker.cancel()
        
        self.workers = []
    
    def enqueue(self, task: Callable[..., Coroutine], *args, **kwargs) -> asyncio.Future:
        """
        Ajouter une tâche à la file d'attente.
        
        Args:
            task: La fonction asynchrone à exécuter.
            *args: Arguments positionnels pour la fonction.
            **kwargs: Arguments nommés pour la fonction.
            
        Returns:
            Un objet Future représentant le résultat de la tâche.
        """
        global _main_event_loop
        
        if _main_event_loop is None:
            init_async_support()
        
        # Créer un Future pour le résultat
        future = asyncio.Future(loop=_main_event_loop)
        
        # Ajouter la tâche à la file d'attente
        asyncio.run_coroutine_threadsafe(
            self.queue.put((task, args, kwargs, future)),
            _main_event_loop
        )
        
        return future

async def gather_with_concurrency(limit: int, *tasks: Coroutine) -> List[Any]:
    """
    Exécuter plusieurs coroutines avec une limite de concurrence.
    
    Args:
        limit: Nombre maximum de coroutines à exécuter simultanément.
        *tasks: Les coroutines à exécuter.
        
    Returns:
        Liste des résultats des coroutines.
    """
    semaphore = asyncio.Semaphore(limit)
    
    async def semaphore_task(task):
        async with semaphore:
            return await task
    
    return await asyncio.gather(*(semaphore_task(task) for task in tasks))

async def wait_for_with_timeout(tasks: List[Coroutine], timeout: float) -> Dict[str, Union[List[Any], List[Exception]]]:
    """
    Attendre l'exécution de plusieurs coroutines avec un timeout.
    
    Args:
        tasks: Liste des coroutines à exécuter.
        timeout: Timeout en secondes.
        
    Returns:
        Dictionnaire contenant les résultats et les erreurs.
    """
    # Créer des tâches avec un timeout
    tasks_with_timeout = [asyncio.wait_for(task, timeout) for task in tasks]
    
    # Exécuter les tâches et récupérer les résultats/erreurs
    results = []
    errors = []
    
    for i, task in enumerate(tasks_with_timeout):
        try:
            result = await task
            results.append(result)
        except Exception as e:
            errors.append(e)
    
    return {
        "results": results,
        "errors": errors
    }

def create_task(coroutine: Coroutine) -> asyncio.Task:
    """
    Créer une tâche asynchrone dans la boucle d'événements principale.
    
    Args:
        coroutine: La coroutine à exécuter.
        
    Returns:
        La tâche créée.
    """
    global _main_event_loop
    
    if _main_event_loop is None:
        init_async_support()
    
    return asyncio.run_coroutine_threadsafe(coroutine, _main_event_loop)
