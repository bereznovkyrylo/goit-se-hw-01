from __future__ import annotations
from collections import UserDict
from datetime import datetime,timedelta,date
from abc import ABC
import pickle


"""
Field: Базовий клас для полів запису.
Name: Клас для зберігання імені контакту. Обов'язкове поле.
Phone: Клас для зберігання номера телефону. Має валідацію формату (10 цифр).
Record: Клас для зберігання інформації про контакт, включаючи ім'я та список телефонів.
AddressBook: Клас для зберігання та управління записами.
"""

DATE_FORMAT='%d.%m.%Y'

def string_to_date(date_string):
    return datetime.strptime(date_string, DATE_FORMAT).date()

class Record():
    def __init__(self,name):
        self.name=Name(name)
        self.phones:list[Phone]=[]
        self.birthday:Birthday|None = None

    def add_phone(self,phone:str)->None:
        self.phones.append(Phone(phone))

    def edit_phone(self,old_phone:str,new_phone:str):
        
        searched_phone:Phone|None=self.find_phone(old_phone)

        self.validate_phone_existence(searched_phone)

        if not searched_phone.is_valid_phone(new_phone):
            raise ValueError('Phone number is not valid')
        
        searched_phone.value=new_phone

        
    def find_phone(self,searched_phone:str)->Phone|None:
        for phone in self.phones:
            if phone.value==searched_phone:
                return phone
        else:
            return None
        
    def remove_phone(self,phone):
        searched_phone=self.find_phone(phone)

        self.validate_phone_existence(searched_phone)
        self.phones.remove(searched_phone)

    def validate_phone_existence(self,phone):
        if phone is None:
            raise ValueError('Phone not found')

            
            
    def add_birthday(self,date):
        self.birthday=Birthday(date)
    def get_birthday(self):
        return getattr(self.birthday,'value',None)
    def get_phones(self):
        return '; '.join(phone.value for phone in self.phones)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {self.get_phones()}, birthday:{self.get_birthday()}"

class AddressBook(UserDict):

    def add_record(self,record:Record):
        name=record.name.value
        self.data[name]=record

    def find(self,name:str)->Record|None:
        return self.data.get(name)
    
    def delete(self,name:str):
        searched_address=self.find(name)

        if searched_address is None:
            raise ValueError('No such address')
            
        self.data.pop(name)

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays=[]
        today = date.today()

        for user in self.data.values():
            user_birthday=user.get_birthday()

            if user_birthday is None:
                continue

            user_birthday_date=string_to_date(user_birthday)
            birthday_this_year = user_birthday_date.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = user_birthday_date.replace(year=(today + timedelta(days=days)).year)

            if  0 <= (birthday_this_year - today).days <= days:
                name=user.name.value
                birthday=user.birthday.value
                weekday=birthday_this_year.weekday()

                if weekday>=5:
                    days_to_monday=7-weekday
                    celebration_day=birthday_this_year + timedelta(days=days_to_monday)
                    birthday=celebration_day.strftime(DATE_FORMAT)

                upcoming_birthdays.append({'name':name,'birthday':birthday})


        return upcoming_birthdays
    def __str__(self):
        return '\n'.join(f'{str(value)}' for value in self.data.values())



class Field(ABC):

    def __init__(self,value):
        self.value=value

    def __str__(self):
        return str(self.value)

class Name(Field):
    ...

class Phone(Field):
    phone_number_length=10
    def __init__(self,phone:str): 
        if self.is_valid_phone(phone):
            super().__init__(phone)
        else:    
            raise ValueError('Wrong phone number')
        
    def is_valid_phone(cls,phone:str)->bool:
        return len(phone)==cls.phone_number_length and phone.isdigit()

class Birthday(Field):
    def __init__(self, date):
        try:
            _=datetime.strptime(date,DATE_FORMAT) # Validate format
            super().__init__(date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


def input_error(func):
    def inner(*args,**kwargs):
        try:
           return func(*args,**kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return 'Wrong command'
        except IndexError:
            return 'Enter the argument for the command'
        except AttributeError:
            return 'Contact not found'
        except Exception as e:
            return f'Error: {e}'
    return inner

    
@input_error
def parse_input(string):
    command,*args=string.split()
    return command.lower(),*args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)

    return message


@input_error
def change_contact(args,book:AddressBook):
    
    name,old_phone,new_phone,*_=args
    record = book.find(name)
    
    record.edit_phone(old_phone,new_phone)
    return "Contact updated."
    
@input_error
def remove_phone(args,book:AddressBook):
    name,phone,*_=args
    record = book.find(name)
    
    record.remove_phone(phone)
    return "Phone removed."
    
@input_error
def show_phone(args,book:AddressBook):
    name,*_=args
    record = book.find(name)

    return f"Phones: {record.get_phones()}"

@input_error
def show_all(book:AddressBook):
    return book if book.data else 'No contacts'

@input_error
def add_birthday(args,book:AddressBook):
    name,date,*_=args
    record=book.find(name)
    
    record.add_birthday(date)
    return 'Birthday added'

@input_error
def show_birthday(args,book:AddressBook):
    name,*_=args
    record=book.find(name)
    
    date=getattr(record.birthday,'value',None)

    if date is None:
        return ValueError('Birthday was not added')

    return date

@input_error
def birthdays(book:AddressBook):
    upcoming_birthdays=book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return 'No upcomming birthdays'
    return f'{upcoming_birthdays}'
        
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename,'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return AddressBook()
    
def save_data(book,filename="addressbook.pkl") :
    with open(filename,'wb')as file:
        pickle.dump(book,file)
