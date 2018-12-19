# Django Coffee Machine Simulator

Project was created due to interview process. Requirements for project:
* Algorithm correctness
* Clean coding
* Well-crafted domain model
* Testing


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 


### Installing

#### Clone
* Clone this repository to your local machine using ```https://github.com/Dejna93/django-coffee-machine.git```

#### Setup
* Move to project root
```
cd django-coffee-machine
```

* Create own virtualenv
```virtual ```

```
virtualenv venv
```

* Install requirements

```
pip install -r requirements/development.txt
```

* Migrate sqlite database
```
python manage.py migrate
```

* Load fixtures
```
python manage.py loaddata coffee.json
```
## Running the tests

Normal django test

```
python manage.py test
```

#### Run coverage test

* Run coverage

```
coverage run --source='.' manage.py test
```
* Report html 
```
coverage html
```

## Deployment

In progress

## Built With

* [Django](https://docs.djangoproject.com/en/1.11/) - The web framework used

## Authors

* **Damian Holuj** - [GitHUB](https://github.com/dejna93)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
