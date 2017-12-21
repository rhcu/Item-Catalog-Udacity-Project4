from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import User, Genre, Base, BookItem

engine = create_engine('sqlite:///new_book_catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()
# the first user
User1 = User(name="Assiya Kh", email="assiyakhuzyakhmetova@gmail.com",
             picture='https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/User_icon_2.svg/220px-User_icon_2.svg.png')
session.add(User1)
session.commit()

# Poetry Books
genre1 = Genre(user_id=1, name="Poetry", description = "Poetry is an art form in which human language is used for its aesthetic qualities in addition to, or instead of, its notional and semantic content.")

session.add(genre1)
session.commit()

book = BookItem(user_id=1, name="Where the Sidewalk Ends", description="Children\'s poetry collection written and illustrated by Shel Silverstein. Published by Harper and Row Publishers.",
                     type = "eBook", price="$2.50", author="Shel Silverstein", genre=genre1)

session.add(book)
session.commit()


book1 = BookItem(user_id=1, name="Leaves of Grass", description="The seminal work of one of the most influential writers of the nineteenth century.",
                     type="hardCopy",price="$3.50", author="Walt Whitman", genre=genre1)

session.add(book1)
session.commit()

book2 = BookItem(user_id=1, name="Howl and Other Poems", description="The single most influential poetic work of the post-World War II era, with over 900,000 copies now in print.",
                     type="hardCopy",price="$5.50", author="Allen Ginsberg", genre=genre1)

session.add(book2)
session.commit()

book3 = BookItem(user_id=1, name="Ariel", description="The beloved poet\'s brilliant, provoking, and always moving poems, including Ariel",
                     type = "eBook",price="$3.50", author="Sylvia Plath", genre=genre1)

session.add(book3)
session.commit()

book4 = BookItem(user_id=1, name="Paradise Lost", description="One of the greatest epic poems in the English language.",
                     type="hardCopy",price="$8.50", author="John Milton", genre=genre1)

session.add(book4)
session.commit()

book5 = BookItem(user_id=1, name="The Odyssey", description="Literature\'s grandest evocation of life's journey, and an individual test of moral endurance",
                     type = "eBook",price="$1.50", author="Homer", genre=genre1)

session.add(book5)
session.commit()

book6 = BookItem(user_id=1, name="The Iliad", description="One of the greatest war stories of all time",
                     type="hardCopy",price="$1.50", author="Homer", genre=genre1)

session.add(book6)
session.commit()


# Fantasy books
genre2 = Genre(user_id=1, name="Fantasy", description="Fantasy is a genre of fiction set in a fictional universe, often, but not always, without any locations, events, or people referencing the real world.")

session.add(genre2)
session.commit()
book7 = BookItem(user_id=1, name="The Chronicles of Narnia", description="Journeys to the end of the world, fantastic creatures, and epic battles between good and evil",
                     type="hardCopy",price="$3.50", author="C.S. Lewis ", genre=genre2)

session.add(book7)
session.commit()

book8 = BookItem(user_id=1, name="The Final Empire", description="In a world where ash falls from the sky, and mist dominates the night, an evil cloaks the land and stifles all life.",
                     type = "eBook",price="$5.50", author="Brandon Sanderson", genre=genre2)

session.add(book8)
session.commit()

book9 = BookItem(user_id=1, name="A Game of Thrones", description="Summers span decades. Winter can last a lifetime. And the struggle for the Iron Throne has begun.",
                     type="hardCopy",price="$3.50", author="George R.R. Martin", genre=genre2)

session.add(book9)
session.commit()

book10 = BookItem(user_id=1, name="Eragon", description="Eragon must navigate the dangerous terrain and dark enemies of an empire ruled by a king whose evil knows no bounds. ",
                     type = "eBook",price="$8.50", author=" Christopher Paolini ", genre=genre2)

session.add(book10)
session.commit()


# Horror books
genre3 = Genre(user_id=1, name="Horror", description="Horror is a genre of fiction which is intended to, or has the capacity to frighten, scare, disgust, or startle its readers or viewers by inducing feelings of horror and terror. ")

session.add(genre3)
session.commit()
book11 = BookItem(user_id=1, name="Into the Drowning Deep", description="Seven years ago, the Atargatis set off on a voyage to the Mariana Trench to film a mockumentary bringing to life ancient sea creatures of legend.",
                     type="hardCopy",price="$7.50", author="Mira Grant", genre=genre3)

session.add(book11)
session.commit()
book12= BookItem(user_id=1, name="Regression", description="Plagued by ghastly waking nightmares, Adrian reluctantly agrees to past life regression hypnotherapy. ",
                     type = "eBook",price="$6.50", author="Cullen Bunn", genre=genre3)

session.add(book12)
session.commit()

book13 = BookItem(user_id=1, name="Her Body and Other Parties", description="Book demolishes the arbitrary borders between psychological realism and science fiction, comedy and horror, fantasy and fabulism. ",
                     type="hardCopy",price="$8.50", author="Carmen Maria Machado", genre=genre3)

session.add(book13)
session.commit()


# Children books
genre4 = Genre(user_id=1, name="Children's", description="Children's literature or juvenile literature includes stories, books, magazines, and poems that are enjoyed by children.")

session.add(genre4)
session.commit()


book14= BookItem(user_id=1, name="Where's the Unicorn?", description="A Magical Search-and-Find Book ",
                     type="hardCopy",price="$1.50", author="Paul Moran", genre=genre4)

session.add(book14)
session.commit()

book15= BookItem(user_id=1, name="The Lost Words", description="Gorgeous to look at and to read. Give it to a child to bring back the magic of language - and its scope",
                    type = "eBook", price="$9.50", author="Robert Macfarlane", genre=genre4)

session.add(book15)
session.commit()


# History books
genre5 = Genre(user_id=1, name="History", description="Historical fiction is a literary genre in which the plot takes place in a setting located in the past. ")

session.add(genre5)
session.commit()

book16= BookItem(user_id=1, name="Sapiens: A Brief History of Humankind", description="The Sunday Times number 1 bestseller",
                     type = "eBook",price="$3.50", author="Yuval Noah Harari", genre=genre5)

session.add(book16)

session.commit()
book17= BookItem(user_id=1, name="The Crusades: A History From Beginning to End", description="Understanding the Crusades is key in understanding the religious divides that still threaten the order of the world. ",
                     type="hardCopy",price="$1.50", author="Hourly History ", genre=genre5)

session.add(book17)
session.commit()

# Comics books
genre6 = Genre(user_id=1, name="Comics", description="Comics is a medium used to express ideas by images, often combined with text or other visual information. Comics frequently takes the form of juxtaposed sequences of panels of images.")


session.add(genre6)
session.commit()

book18= BookItem(user_id=1, name="Comic Book Hero: Working with Britain's Picture Strip Legends", description="Comic Book Hero tells the inside story of how Barrie Tomlinson built up a successful boys' publishing group at IPC Magazines",
                     type = "eBook",price="$10.50", author="Barrie Tomlinson", genre=genre6)

session.add(book18)

book19= BookItem(user_id=1, name="Super Graphic: A Visual Guide to the Comic Book Universe", description="The comic book universe is adventurous, mystifying and filled with heroes, villains and ComicCon attendees.",
                     type="hardCopy",price="$3.50", author="Jonh Green", genre=genre6)

session.add(book19)

book20= BookItem(user_id=1, name="Write and Draw Your Own Comics ", description="An awesome activity book for budding comic artists to imagine and draw their own comic strips. ",
                     type="hardCopy",price="$7.50", author="Louie Stowell", genre=genre6)

session.add(book20)

print "DB is populated"