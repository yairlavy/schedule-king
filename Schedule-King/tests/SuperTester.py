import os
import subprocess

class SuperTester:
    def __init__(self):
        # Absolute path to the folder this code is in
        self.folder = os.path.dirname(os.path.abspath(__file__))
        self.test_files = self.find_tests()

    def find_tests(self):
        # Recursively find test_*.py files in self.folder and subfolders
        test_files = []
        for root, _, files in os.walk(self.folder):
            for f in files:
                if f.startswith("test_") and f.endswith(".py"):
                    test_files.append(os.path.join(root, f))
        return sorted(test_files)

    def display_tests(self):
        # Print all the tests in a list (only file names)
        print("Found the following test files:")
        for i, test_file in enumerate(self.test_files, start=1):
            print(f"{i}. {os.path.basename(test_file)}")
        print()

    def parse_input(self, input_str):
        # Parse the user input into test numbers and flags
        input = input_str.strip().split()
    
        flags = []
        testNumbers = []
        show_gui = False  # Default to not show GUI
        qt_wait_time = None # hold the wait time for qt-show default to None
        
        for item in input:
            if item.isdigit():
                testNumbers.append(int(item))
            elif item.startswith('-') or item.startswith('--'):
                flags.append(item)
            elif item.startswith('qt-show'):
                show_gui = True  # If 'qt-show' flag is present, show the GUI
                if ':' in item:
                    try:
                        qt_wait_time = int(item.split(':')[1])
                    except ValueError:
                        print(f"Invalid qt-show wait time: {item.split(':')[1]} \n")
                        return False, None, None, None
            else:
                print(f"Invalid input: {item} \n")
                return False, None, None, None
        
        return testNumbers, flags, show_gui, qt_wait_time

    def build_command(self, testNumbers, flags):
        # Build the command to run pytest with the selected tests and flags
        if testNumbers == [0]:
            selected_tests = self.test_files
        else:
            selected_tests = []
            for n in testNumbers:
                if 1 <= n <= len(self.test_files):
                    selected_tests.append(self.test_files[n - 1])
                else:
                    print(f"Invalid test number: {n} \n")
                    return False
        full_paths = [os.path.join(self.folder, t) for t in selected_tests]
        return ["python", "-m", "pytest"] + full_paths + flags

    def run(self):
        # Main loop to run the tests
        if not self.test_files:
            print("No test files found in this folder.")
            return
        
        while True:
            self.display_tests()
            print("Enter test numbers (0 for all) and optional pytest flags like (-v, -s), qt-show:time for gui window, or 'q' to quit")
            print("Example: 1 2 -v -s qt-show:2 (for show the qt for 2 sec)")
            user_input = input().strip()
            if user_input.lower() in ('q', 'quit', 'exit'):
                break

            try:
                testNumbers, flags, show_gui, qt_wait_time = self.parse_input(user_input)
                if not testNumbers:  # Continue if invalid input
                    continue

                command = self.build_command(testNumbers, flags)
                if not command:
                    continue

                # Set the environment variable to hide the window by default
                env = os.environ.copy()
                
                # Add the project root to PYTHONPATH so that pytest can find the modules
                project_root = os.path.abspath(os.path.join(self.folder, ".."))
                env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

                if not show_gui:
                    env["QT_QPA_PLATFORM"] = "offscreen"  # Hide GUI
                
                # If qt-show is specified, set the wait time
                if qt_wait_time is not None:
                    env["WAIT_TIME"] = str(qt_wait_time)

                print(f"Running: {' '.join(command)}\n")
                subprocess.run(command, env=env)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    tester = SuperTester()
    tester.run()