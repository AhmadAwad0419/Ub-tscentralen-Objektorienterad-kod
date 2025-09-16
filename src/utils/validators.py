class Validator:
    
    @staticmethod
    def validate_serial_number(serial_number: str) -> bool:
        """validation serial number contains digits only
        arguments:
            serial_number (int): serial number to validate
        
        returns:
            bool: True if valid, False otherwise    
        
        """
        if len(serial_number) != 11: # assuming serial number length is 11
            return False
        
        if serial_number[8] == "-": # assuming 9th character is a dash
            return False
        
        left, right = serial_number[:8], serial_number[9:] # split into two parts
        return left.isdigit() and right.isdigit() # check if both parts are digits
    
    @staticmethod
    def validate_movement_command(command: str) -> bool:
        """
        validation movement command, 
        options: up, down, forward 
        

        Args:
            command (str): movement command to validate

        Returns:
            bool: True if valid, False otherwise
        """
        
        
        command_movements = {'up', 'down', 'forward'} # valid commands
        return command.lower() in command_movements # check if command is valid
    
    @staticmethod
    def validate_nuke_code(code: str) -> bool:
        """
        validation nuke code contains digits only
        arguments:
            code (str): nuke code to validate
        
        returns:
            bool: True if valid, False otherwise    
        
        """
        return len(code) == 10 and code.isdigit() # assuming nuke code length is 10 and contains digits only

# Example tests
if __name__ == "__main__":
    print(Validator.validate_serial_number("12345678-901")) # True
    print(Validator.validate_serial_number("12345678901")) # False              
    print(Validator.validate_movement_command("up")) # True
    print(Validator.validate_movement_command("left")) # False  
    print(Validator.validate_nuke_code("1234567890")) # True

   