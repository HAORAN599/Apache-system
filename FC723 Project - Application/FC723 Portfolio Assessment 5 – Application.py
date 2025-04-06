# Import necessary libraries
import json  # For reading and writing JSON files
import random  # For generating random booking codes
import string  # For using letters and digits
import sys  # For system exit
import sqlite3  # For interacting with the database


class BookingSystem:
   def __init__(self):
    # original connection with data base
      self.data_file = "booking.json"  # JSON file for seat map and used codes
      self.load_data()   # Load data from file
      self.seat_type = {'A': 'window','B': 'middle','C': 'aisle','D': 'aisle','E': 'middle','F': 'window'}  # Mapping seat letters to seat types
   
      self.conn = sqlite3.connect("bookings.db")  # Set up the SQLite database connection
      self.cursor = self.conn.cursor()
      self.create_table()
   
   def create_table(self):  # Create the database table to store booking info
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                reference_code TEXT PRIMARY KEY,
                seat TEXT,
                passport TEXT,
                first_name TEXT,
                last_name TEXT
            )
        ''')
        self.conn.commit()
   
   def load_data(self):   # Load seat map and booking codes from the JSON file
       try:
            # try to open JSON and loading data
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.seat_map = data.get('seat_map', {})
               
                self.used_booking_codes = set(data.get('used_codes', []))
                
                self.bookings = data.get('bookings', [])
       except FileNotFoundError:   
            # If the file does not exist, initialize the seating map, the used code collection, and the booking record
            self.seat_map = self.original_seat_map()
           
            self.bookings = []
            self.used_booking_codes = set()
            # save original file
            self.save_data()
            
   def save_data(self):   # Save seat map and bookings into the JSON file
        # set up dictionary
        data = {
            'seat_map': self.seat_map,
            'used_codes': list(self.used_booking_codes),
            'bookings': self.bookings
        }
        # write data in JSON 
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)

   def original_seat_map(self):   # Create the original seat map for all 80 rows and 6 columns
    seat_map = {}
    for row in range(1, 81):
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat = f'{row}{col}'
            # Mark  77，78 as storage
            if row in [77, 78] and col in ['D', 'E', 'F']:
                seat_map[seat] = 'Storage'
            else:
                seat_map[seat] = 'F'
    
    return seat_map

   def show_all_seats(self):  # Display seat status for all seats in the plane
    print("The status of all seats is as follows:\n")
    for row in range(1, 81):
        row_display = f"Row {row}: "
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat = f"{row}{col}"
            status = self.seat_map.get(seat, "Unknown")
            
            if status == "F":    # Decide how to display each seat status
                display_status = "F"
            elif status == "Storage":
                display_status = "S"
            else:
              status.startswith("R")   # This is a booking reference
              display_status = "Booked"   
            
            row_display += f"{seat}:{display_status} "
        print(row_display)

   
   def check_seat_availability(self):    # Let user check and optionally book a seat
       while True:    #use while loop to seat whether available
           #use upper and strip to avoid space and different case
           seat = input("please enter seat number to check weather it is availability(enter K to exit) : ").upper().strip()    
           if seat == 'K':
               break
           
           if seat in self.seat_map:
              if self.seat_map[seat] == "F":
                  print(f"seat {seat} status is: Available")
              else:
                  print(f"seat {seat} status is: booked")
           
              if self.seat_map[seat] == "F":
              
                 while True: 
                   confirm = input("Do you want to book it? (yes/no): ").lower().strip() #use upper and strip to avoid space and different case
                   if confirm == "yes":
                      self.book_seat(seat)
                      return   # Call the reservation method and pass in the seat number
                   elif confirm != "no":
                      print("Can not understand,please try again")   
                   else:
                      break
                     
           else:
              print("Can not find this seat,please try again.")
            
   
   def generate_booking_code(self,length = 8):   # Generate a unique 8-character reference code
      while True: 
        characters = string.ascii_letters + string.digits
    # Randomly select 8 characters from the character set
        reference_code = ''.join(random.choices(characters, k=length))
        
        if reference_code not in self.used_booking_codes:
            self.used_booking_codes.add(reference_code)
            return reference_code
            
        else:
            continue
       
    
   def book_seat(self,seat):    # Book a specific seat and collect passenger info
     
        if seat in self.seat_map:
            print("this seat is available, please eneter your name and passport")
            first_name = input("first name: ").strip()
            last_name = input("last_name: ").strip()
            passport = input("passport number: ").strip()
            reference_code = self.generate_booking_code()
            self.seat_map[seat] = f"R{reference_code}"    # Mark the seat as booked in seat_map and save the reservation code (in Rxxxxxxx format)
           # Save passenger info to the database
            self.cursor.execute('''
                INSERT INTO bookings (reference_code, seat, passport, first_name, last_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (reference_code, seat, passport, first_name, last_name))
            self.conn.commit()  # Commit the transaction to save your changes
           
            self.bookings.append({
             "reference_code": reference_code,
             "seat": seat,
             "passport": passport,
             "first_name": first_name,
             "last_name": last_name
         })
        
            self.save_data()   # Also add booking information to the bookings list in local memory (for JSON save)
            print(f"booking successful！Your reference code is：{reference_code}")
            
            while True:     # Ask if they want to book another seat
               rebook_confirm = input("Do you want to book any other seat?(yes/no): ").lower().strip() #use upper and strip to avoid space and different case
               if rebook_confirm == "yes":
                   self.book_seat_flow()
                   return
               elif rebook_confirm == "no":
                   print("Thanks for your booking,back to menu.")
                   return  
               else:
                   print("Can not understand,please try again: ")
                   
               
        else:
            while True:   # If the seat is invalid or does not exist in seat_map
              ask_user = input("this seat is not available or enter type error,please enter 'try again' or 'back to menu': ").lower() #use lower to avoid different case
              if ask_user ==  "try again":
                  break   # Return to the main loop and re-enter the seat number
              elif ask_user == "back to menu":
                  break   # Return directly to the main menu
              else:
                  print("Can not understand,please try again")
                  continue
              

                       
            
   def book_seat_flow(self):   # Start booking flow where user enters the seat to book
     while True:
        seat = input("Please enter the seat number you want to book (or K to return to menu): ").upper().strip() #use upper and strip to avoid space and different case
        if seat == 'K':
            return
        if seat not in self.seat_map:
           print(" Invalid seat number. Please try again.")
           continue
        if self.seat_map[seat] in ['X', 'S']:
           print(f"Seat {seat} is not a valid seat for booking (aisle or storage).")
           return
        
        row = int(seat[:-1])
        col = seat[-1]
        if row in [77, 78] and col in ['D', 'E', 'F']:   # Block storage seats
            print("This seat is in a storage area and cannot be booked.")
            continue
        

        elif not self.seat_map[seat].startswith("F"):
           print(f" Seat {seat} is already booked.")    
        
        else: 
          self.book_seat(seat)
          return

   def cancel_booking(self):     # Cancel a booking by reference code
    cancel_code = input("Please enter the 'reference code' from your booking confirmation: ").strip() #use strip to avoid space 

    booking_to_cancel = None
    for b in self.bookings:
        if b["reference_code"] == cancel_code:
            booking_to_cancel = b
            break

    if booking_to_cancel:
        confirm = input(f"Are you sure you want to cancel booking {cancel_code} for seat {booking_to_cancel['seat']}? (yes/no): ").lower().strip()
        if confirm == "no":
            print("Cancellation aborted.")
            return
        elif confirm == "yes":
            seat = booking_to_cancel["seat"]
            self.seat_map[seat] = 'F'    # Reset seat to free

            # Delete the corresponding record from the database
            self.cursor.execute("DELETE FROM bookings WHERE reference_code = ?", (cancel_code,))
            self.conn.commit()

            self.bookings = [b for b in self.bookings if b["reference_code"] != cancel_code]
            self.used_booking_codes.discard(cancel_code)
            self.save_data()

            print(f"Booking {cancel_code} has been cancelled. Seat {seat} is now available.")
        else:
            print("Can not understand, please try again.")
            return
    else:    # Try to find booking only in the Data base,avoid json do not have but data base have
        
        self.cursor.execute("SELECT seat FROM bookings WHERE reference_code = ?", (cancel_code,))
        result = self.cursor.fetchone()

        if result:       #Confirm that the user needs to cancel again to prevent accidental deletion
            seat = result[0]    
            confirm = input(f"Booking found in database for seat {seat}. Do you want to cancel it? (yes/no): ").lower().strip()
            if confirm == "yes":
                self.seat_map[seat] = 'F'
                self.cursor.execute("DELETE FROM bookings WHERE reference_code = ?", (cancel_code,))
                self.conn.commit()
                self.used_booking_codes.discard(cancel_code)
                self.save_data()
                print(f"Booking {cancel_code} has been cancelled from database. Seat {seat} is now available.")
            else:
                print("Cancellation aborted.")
        else:
            print("Booking code not found.")


           
      
           
   def filter_seats_type(self):   # Let user choose and view available seats by seat type
       while True:    # Prompts the user to enter the desired seat type, window/aisle/middle is supported, you can also enter K to exit
        seat_type = input("please enter which type seat you prefer(window/aisle/middle),(enter K is exit): ").strip().lower()
         
        if seat_type == "k":
              break
        elif seat_type != "window" and seat_type != "aisle" and seat_type != "middle":  # If the content entered is not a valid three seat types, an error message is displayed and re-enter
              print("Can not understand,please try again")
              continue
        
        
        elif seat_type == "window":
            
              print("Available window seats:")
              seat_shown = []
              for seat, status in  self.seat_map.items():
                  if seat[-1] in ['A', 'F'] and status == 'F':   # Filter out the seats that end with A or F and the status is F (empty seat)
                      # Further exclude Storage or invalid areas (Storage or X)
                      if self.seat_map.get(seat) not in ['Storage', 'X']:  
                         seat_shown.append(seat) 
              
                # Displays two seats per row for a more orderly layout
              for i in range(0,len(seat_shown),2):
                  print("  ".join(seat_shown[i: i + 2]))
                  
        elif seat_type =="aisle":
              seat_shown = []
              print("Available aisle seats:")
              for seat, status in self.seat_map.items():
                  if seat[-1] in ['C', 'D'] and status == 'F':  
                     if self.seat_map.get(seat) not in ['Storage', 'X']: 
                        seat_shown.append(seat)
                        
              for i in range(0,len(seat_shown),2):
                 print("  ".join(seat_shown[i: i + 2]))
        
        else:
            seat_shown = []  
            print("Available middle seats:")
            for seat, status in self.seat_map.items():
                  if seat[-1] in ['B', 'E'] and status == 'F':  
                      if self.seat_map.get(seat) not in ['Storage','X']:  
                          seat_shown.append(seat)
            
            for i in range(0,len(seat_shown),2):
                 print("  ".join(seat_shown[i: i + 2]))


   def main_menu(self):  # Main course menu loop, users through the digital selection function
        while True:
            print("\nSeat Booking Menu:")
            print("1. Check seat availability")
            print("2. Book a seat")
            print("3. Cancel a booking")
            print("4. Show all seat statuses")
            print("5. Filter seats by type")
            print("6. Exit")
            choice = input("Enter your choice: ").strip()  # Call the corresponding function method according to the user's choice
            if choice == "1":
                self.check_seat_availability()
            elif choice == "2":
                self.book_seat_flow()
            elif choice == "3":
                self.cancel_booking()
            elif choice == "4":
                self.show_all_seats()
            elif choice == "5":
                self.filter_seats_type()
            elif choice == "6":
                print("Exiting the system. Goodbye!")
                self.conn.close()
                sys.exit()
            else:
                print("Invalid choice, please try again.")

if __name__ == "__main__":  #If this file is the main program (not referenced by another module), create the system object and run the main menu
    system = BookingSystem()  # Create an instance of the booking system
    system.main_menu()   # Launch the main menu to allow users to interact


    