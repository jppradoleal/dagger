# Dagger

Dagger its a CRUD to manage liquor stores, it uses GIS to allow the user to search for nearby liquor stores. The project also uses Github Actions to enforce codestyle, lint, apply integration tests, upload the docker image, and (futurely) define the infrastructure using terraform, ArgoCD and K8s. 

# Dependencies
* FastAPI
* SQLAlchemy
* Alembic
* JWT
* Docker
* Kubernetes
* Helm
* Terraform
* AWS

## Dev dependencies
* Ruff
* Black
* Isort
* Github Actions
* Pytest
* Poetry

# TODO

- [x] Basic API setup
- [x] Pre-commit setup
- [x] Docker setup
- [x] SQLAlchemy + Alembic setup
- [x] Auth endpoint
- [x] Auth tests
- [x] CI Pipeline setup
- [x] Create adega endpoint
- [x] List adegas endpoint
- [x] Search adegas endpoint
- [x] Authentication
- [ ] Kubernetes cluster definition
- [ ] Terraform infrastructure definition
- [ ] CD Pipeline setup
