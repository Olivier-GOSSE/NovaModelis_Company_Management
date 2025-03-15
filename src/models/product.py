"""
Product model for the application.
"""
import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, DateTime, Boolean, Enum, Text
from sqlalchemy.orm import relationship
import datetime

from database.base import Base


# Association table for product-country relationship (many-to-many)
product_country = Table(
    'product_country',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('country_id', Integer, ForeignKey('countries.id'), primary_key=True)
)


class Country(Base):
    """
    Country model.
    """
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(2), nullable=False, unique=True)  # ISO 3166-1 alpha-2 code
    
    # Relationships
    products = relationship("Product", secondary=product_country, back_populates="countries")
    sales = relationship("Sale", back_populates="country")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Country(name='{self.name}', code='{self.code}')>"


class Product(Base):
    """
    Product model.
    """
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    image_path = Column(String(255))
    production_time = Column(Float, nullable=False)  # in hours
    production_cost = Column(Float, nullable=False)  # in currency units
    initial_quantity = Column(Integer, default=0)
    
    # Relationships
    countries = relationship("Country", secondary=product_country, back_populates="products")
    sales = relationship("Sale", back_populates="product")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Product(name='{self.name}', production_cost={self.production_cost})>"
    
    @property
    def total_sales(self):
        """
        Get the total number of sales for this product.
        """
        return sum(sale.quantity for sale in self.sales)
    
    @property
    def sales_by_country(self):
        """
        Get a dictionary of sales by country.
        """
        result = {}
        for sale in self.sales:
            country_name = sale.country.name
            if country_name in result:
                result[country_name] += sale.quantity
            else:
                result[country_name] = sale.quantity
        return result


class Sale(Base):
    """
    Sale model for tracking product sales by country.
    """
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    sale_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="sales")
    country = relationship("Country", back_populates="sales")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Sale(product_id={self.product_id}, country_id={self.country_id}, quantity={self.quantity})>"
