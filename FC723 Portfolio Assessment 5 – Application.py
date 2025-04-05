import json
import random
import string
import sys

class booking_system:
   def __init__(self):
    # original connection with data base
      self.data_file = "booking.json"
      self.load_data()
      self.seat_type = {'A': 'window','B': 'middle','C': 'aisle','D': 'aisle','E': 'middle','F': 'window'}
   
   def load_data(self):
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
            
   def save_data(self):
        # set up dictionary
        data = {
            'seat_map': self.seat_map,
            'used_codes': list(self.used_booking_codes),
            'bookings': self.bookings
        }
        # write data in JSON 
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)

   def original_seat_map(self):
    seat_map = {}
    for row in range(1, 81):
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat = f'{row}{col}'
            # 只有第 77 和 78 行的 D/E/F 是存储区
            if row in [77, 78] and col in ['D', 'E', 'F']:
                seat_map[seat] = 'Storage'
            else:
                seat_map[seat] = 'Available'
    
    return seat_map

   def show_all_seats(self):
    print("The status of all seats is as follows:\n")
    for row in range(1, 81):
        row_display = f"Row {row}: "
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat = f"{row}{col}"
            status = self.seat_map.get(seat, "Unknown")
            row_display += f"{seat}:{status} "
        print(row_display)

   
   def check_seat_availability(self):
       while True: 
           seat = input("please enter seat number to check weather it is availability(enter K to exit) : ").upper().strip()
           if seat == 'K':
               break
           
           if seat in self.seat_map:
              print(f"seat {seat} status is: {self.seat_map[seat]}")
           
              if self.seat_map[seat] == "Available":
              
               while True: 
                 confirm = input("Do you want to book it? (yes/no): ").lower().strip()
                 if confirm == "yes":
                    self.book_seat(seat)
                    return# 调用预订方法并传入座位号
                 elif confirm != "no":
                    print("Can not understand,please try again")   
                 else:
                    break
                     
           else:
              print("Can not find this seat,please try again.")
            
   
   def generate_booking_code(self,length = 8):
      while True: 
        characters = string.ascii_letters + string.digits
    # 从字符集中随机选择8个字符
        reference_code = ''.join(random.choices(characters, k=length))
        
        if reference_code not in self.used_booking_codes:
            self.used_booking_codes.add(reference_code)
            return reference_code
            
        else:
            continue
       
    
   def book_seat(self,seat):
     
        if seat in self.seat_map:
            print("this seat is available, please eneter your name and passport")
            first_name = input("first name: ").strip()
            last_name = input("last_name: ").strip()
            passport = input("passport number: ").strip()
            reference_code = self.generate_booking_code()
            self.seat_map[seat] = 'booked'
           
            self.bookings.append({
             "reference_code": reference_code,
             "seat": seat,
             "passport": passport,
             "first_name": first_name,
             "last_name": last_name
         })
        # save data
            self.save_data()
            print(f"booking successful！Your reference code is：{reference_code}")
            
            while True:  
               rebook_confirm = input("Do you want to book any other seat?(yes/no): ").lower().strip()
               if rebook_confirm == "yes":
                   self.book_seat_flow()
                   return
               elif rebook_confirm == "no":
                   print("Thanks for your booking,back to menu.")
                   return  
               else:
                   print("Can not understand,please try again: ")
                   
               
        else:
            while True:
              ask_user = input("this seat is not available or enter type error,please enter 'try again' or 'back to menu': ").lower()
              if ask_user ==  "try again":
                  break
              elif ask_user == "back to menu":
                  break
              else:
                  print("Can not understand,please try again")
                  continue
              

                       
            
   def book_seat_flow(self):
     while True:
        seat = input("Please enter the seat number you want to book (or K to return to menu): ").upper().strip()
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
        if row in [77, 78] and col in ['D', 'E', 'F']:
            print("This seat is in a storage area and cannot be booked.")
            continue
        

        elif self.seat_map[seat] != "Available":
           print(f" Seat {seat} is already booked.")    
        
        else: 
          self.book_seat(seat)
          return

   def cancel_booking(self): 
       cancel_code = input("Please enter the 'reference code' from your booking confirmation: ").strip()
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
       
              self.seat_map[seat] = 'Available'
       
              self.bookings = [b for b in self.bookings if b["reference_code"] != cancel_code]
       
              self.used_booking_codes.remove(cancel_code)

              self.save_data()
              print(f"Booking {cancel_code} has been cancelled. Seat {seat} is now available.")
           
           else:
               print("Can not understand,please try again.")
               return
               
       else:
           print("Booking code not found.")
           
      
           
   def filter_seats_type(self): 
       while True: 
        seat_type = input("please enter which type seat you prefer(window/aisle/middle),(enter K is exit): ").strip().lower()
         
        if seat_type == "k":
              break
        elif seat_type != "window" and seat_type != "aisle" and seat_type != "middle":
              print("Can not understand,please try again")
              continue
        
        
        elif seat_type == "window":
            
              print("Available window seats:")
              seat_shown = []
              for seat, status in  self.seat_map.items():
                  if seat[-1] in ['A', 'F'] and status == 'Available':  
                      
                      if self.seat_map.get(seat) not in ['Storage', 'X']:  
                         seat_shown.append(seat) 
              
                
              for i in range(0,len(seat_shown),2):
                  print("  ".join(seat_shown[i: i + 2]))
                  
        elif seat_type =="aisle":
              seat_shown = []
              print("Available aisle seats:")
              for seat, status in self.seat_map.items():
                  if seat[-1] in ['C', 'D'] and status == 'Available':  
                     if self.seat_map.get(seat) not in ['Storage', 'X']: 
                        seat_shown.append(seat)
                        
              for i in range(0,len(seat_shown),2):
                 print("  ".join(seat_shown[i: i + 2]))
        
        else:
            seat_shown = []  
            print("Available middle seats:")
            for seat, status in self.seat_map.items():
                  if seat[-1] in ['B', 'E'] and status == 'Available':  
                      if self.seat_map.get(seat) not in ['Storage','X']:  
                          seat_shown.append(seat)
            
            for i in range(0,len(seat_shown),2):
                 print("  ".join(seat_shown[i: i + 2]))


   def main_menu(self):
        while True:
            print("\nSeat Booking Menu:")
            print("1. Check seat availability")
            print("2. Book a seat")
            print("3. Cancel a booking")
            print("4. Show all seat statuses")
            print("5. Filter seats by type")
            print("6. Exit")
            choice = input("Enter your choice: ").strip()
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
                
                sys.exit()
            else:
                print("Invalid choice, please try again.")

if __name__ == "__main__":
    system = booking_system()
    
    system.main_menu()
































        