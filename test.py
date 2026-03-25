from datetime import datetime

print("Enter your birthdate (YYYY-MM-DD):")
birthdate = input()

birthdate = datetime.strptime(birthdate, "%Y-%m-%d")

if birthdate.month == datetime.now().month and birthdate.day == datetime.now().day:
    print("Happy birthday! Have a great day!")
else:
    print("***Be Patient***")
    print("Have a great day!")
