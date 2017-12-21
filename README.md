# Udacity Item Catalog Project
The 4th projects made as a part of Udacity Full Stack Web Development Nanodegree.
Project represents a an application that provides a list of items as well as a user registration and authentication system.
Registered users have the ability to use CRUD functionallity, or `post`, `delete`, `edit`.
For User Registration `Google+ Authentification and Authorization service`. `Local Permissions System` was implemented to prevent other user's changes to items uploaded by someone.
# Required software
Vagrant and VirtualBox are needed to be installed before running the program to provide Linux environment. Vagrant can be downloaded from HashiCorp [website](https://www.vagrantup.com/), and VirtualBox from [here](https://www.virtualbox.org/). If you face some problems during the installation of Vagrant, you can find answers either at [Stack OverFlow](https://stackoverflow.com/search?q=vagrant) or in the [GitHub repository](https://github.com/hashicorp/vagrant) of Vagrant itself. 

Also, installed [Python 2.7](https://www.python.org/downloads/) is required, also project uses `SQLAlchemy` Python SQL toolkit and Object Relational Mapper and `Flask` Python Microframework.

Frontend was done with `HTML`, while `JavaScript` and `jQuery` were needed to connect client side to server.
# How to start
* After the installation, download Vagrant Virtual Machine from [here](https://github.com/udacity/fullstack-nanodegree-vm)
* Launch the Virtual Machine by running in command line 
    `vagrant up`
* Enter  your Virtual Machine after the previous command by 
    `vagrant ssh`
* Clone the project from repository to the `catalog` directory in your vagrant folder
* Enter this repository by running 
    `cd /vagrant/catalog`
* Run the python script `application.py` with the following command:
    `python application.py`
* Access an application by visiting `http://localhost:8000/` locally 
# BookShelf Item Catalog Application
Database contains three tables: 
`genre`, `user`, `book_item`.
Each BookItem belongs to specific Genre, while each User can create both Genre and BookItem in it. Different Users can add BookItems to the Genre,
however, only creator can edit or delete created Genres and BookItems. Not registered users are not able to add, delete or edit anything, but they can see publicly available list of items, which are rendered with `public_genres.html` and `public_books.html`. If authentificated user tries to edit or delete items that were added by another user, alertwindow is shown and the action is aborted.

Each BookItem contains the following attributes: ID (Primary Key), Name, Author, Description, Price, Type (either eBook or HardCopy), GenreID(ForeignKey), UserID(ForeignKey), while Genre has ID (Primary Key), Description, UserID (ForeignKey), User has ID (Primary), Name, Email and Picture that are taken from Google+ account after authentification. 

Python file `populate_book.py` was used to add items to the `new_book_catalog.db` file.

## Demonstration
Screenshots of some pages along with their URL adresses are shown below
![http://localhost:8000/](https://pp.userapi.com/c840625/v840625567/36dbb/dBLiYk0Xhho.jpg) 
http://localhost:8000/ or http://localhost:8000/genres (authorized)
![http://localhost:8000/](https://pp.userapi.com/c840625/v840625567/36d77/DBWi1F8bC9c.jpg) 
http://localhost:8000/ or http://localhost:8000/genres (not authorized used)
![http://localhost:8000/genres/1/books](https://pp.userapi.com/c840625/v840625567/36d81/XElRvk0k0o4.jpg) 
http://localhost:8000/genres/1/books (authorized) shows all books of Poetry (GenreId=1) genre for an authorized user.
## License
Was built as a part of [Udacity Full Stack Web Developer Nanodegree Program](https://www.udacity.com/)
