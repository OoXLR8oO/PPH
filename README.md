# Film Processing Dashboard

A FastAPI-based web application for managing film processing orders and customers.

This project combines a REST API with a server-rendered frontend to handle basic order management workflows.

## Overview

The system allows you to:

- Create and manage customer records
- Create film processing orders linked to customers
- Track order details such as film type and print requirements
- View and edit orders through a simple dashboard interface
- Search and filter customers and orders

## Architecture

The project is split into two main parts:

- **API layer** (`/api`)
  - FastAPI routers for orders and customers
  - Async SQLAlchemy ORM models
  - PostgreSQL database integration

- **Frontend layer** (`/frontend`)
  - Server-rendered pages using Jinja2 templates
  - Basic token-based authentication
  - Simple dashboard UI for interacting with the system

## Key Technologies

- FastAPI
- SQLAlchemy (async ORM)
- PostgreSQL
- Jinja2 templates
- Token-based authentication
- Alembic (database migrations)

## Project Structure

- `api/` – database models, schemas, routes, and business logic
- `frontend/` – HTML templates and page routes
- `alembic/` – database migrations
- `main.py` – application entry point

## Notes

This project is intended as a learning and portfolio piece demonstrating full-stack backend development with FastAPI, including database design, async patterns, and basic frontend integration.
