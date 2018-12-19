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
* [Jquery](https://api.jquery.com/) - Javascript framework used

## Authors

* **Damian Holuj** - [GitHUB](https://github.com/dejna93)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


## Some words from author

My main goal was separation simulation logic from Django, because it is possible to use whole logic in other framework or in another way.
After analysis how coffee machine works, I choice the most basic and required parts to implemented.
To simplify implementation and work i create abstract class, which connected all parts. Provides basics operation on each device.
Later i implemented a whole models and logic for control devices.  
Next big problem was how to implement algorithm brewing coffee for three kind of coffee.
I want find solution that didn`t required changes in core mechanism to implement each kind of coffee.
Thats why i choice design pattern called strategy. Strategy instead of implementing  a single algorithm directly,
code receives runtime instruction which kind of algorithm to use. 
Now fronted, every device needs to have some interface to react for some kind of action. 
I implemented ajax view handle each operation via ajax without refresh page. 
Every implemented action from making coffee to fill water is handle by ajax in froneted 
and backend send response via json.  