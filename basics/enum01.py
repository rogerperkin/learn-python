from enum import Enum 

class Color(Enum):
    RED: str = 'R'
    GREEN: str = 'G'
    BLUE: str = 'B'

print(Color('G'))
print(Color('R'))

# Define values for each colour 

# One use of Enum is for match case instead of else if statements, match the statement and then case is 
# action to perform 

def create_car(color: Color) -> None: 
    match color: 
        case Color.RED:
            print(f'Your car is Red')
        case _:
            print(f'Invalid Option')





    
