import time


class Timer():

    def __init__(self):
        self.start_time = time.time()

    def start(self):
        last_time = self.start_time
        lap_num = 1
        value = ""

        print("Press ENTER for each lap.\nType Q and press ENTER to stop.")

        while value.lower() != "q":
            # Input for the ENTER key press
            value = input()

            # The current lap-time
            lap_time = round((time.time() - last_time), 2)

            # Total time elapsed since the timer started
            total_time = round((time.time() - self.start_time), 2)

            # Printing the lap number, lap-time, and total time
            print("Lap No. " + str(lap_num))
            print("Total Time: " + str(total_time))
            print("Lap Time: " + str(lap_time))

            print("*" * 20)

            # Updating the previous total time and lap number
            last_time = time.time()
            lap_num += 1

        print("Exercise complete!")

    def stop(self):
        """Stop the timer, and report the elapsed time"""
