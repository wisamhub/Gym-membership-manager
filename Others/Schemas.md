-ER schema:
1) Person(ID, Name, Gender, Address, Bdate, Email, tele)
2) Member(M_ID, ID, Subscription Date, Monthly/Yearly, Rank)
3) Staff(SSN, ID, HireDate, Salary)
4) Worker(SSN, Type)
5) Coach(SSN, Type)

-PK and FK: (PK is primary key, FK is foreign key)
In 1: ID is the primary key
In 2: M_ID is PK and ID is FK from Person
In 3: SSN is PK and ID is FK from person
In 4 and 5: SSN is both PK and FK from Staff

-Relational Schema:
All entity schemas do not change.
