#!/usr/bin/python3

"""
Emission Data Analyzer by dotrebski

This script allows the user to process and analyze a CSV file of a specific design in mind. The script:
 * verifies whether a non-empty CSV file with the provided name exists;
 * initializes an object with the data from that file facilitating analysis and other operations;
 * analyzes any year in the file's range in terms of minimal, maximal and average values;
 * visualizes the data related to one to two countries, using Matplotlib;
 * verifies whether the data in the initialized object adheres to the specific design described below;
 * and finally, extracts at least one country and the associated data into a subset CSV file.

The script requires that `NumPy` and `Matplotlib` be installed within the Python environment the script is run in.
According to vermin, the minimum required version of Python to run the script is 3.6. This file can also be imported
as a module.

The specific design mentioned above is that:
 1) the first row should contain a range of years;
 2) the following rows should contains decimal values;
 3) optionally, the first column of the first row should say what the file represents (e.g., CO2 per capita);
 4) the first column of the following rows should each contain a different country's name with proper capitalization.

Created in the course of the guru99 Python project, with the constraint that `pandas` could not be used
in the implementation. As a **beginner**, I found it very challenging. However, in the end, it was a very satisfactory
exercise, as well. I'm not planning on expanding the design at the moment.
"""

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from os.path import exists, splitext


class AnalysisCSV:
    """
    A class used to conveniently process the data in a CSV file.

    Methods:
        @staticmethod
        get_file(prompt: str) -> str:
            Prompts the user to enter a CSV filename, checks if a non-empty file like that exists, and returns its name.

        __init__(self, filename: str) -> None:
            Initialize an object with the filename, data_dict, countries, first_key and first_value attributes.

        get_year(prompt: str) -> int:
            Prompts the user to enter a year in the range of self.first_value, inclusive. Returns the year.

        get_country(self, prompt: str, num: int, strict: bool = True) -> list[str]
            Prompts the user to enter a comma-separated string of countries and returns their list if they are correct.

        extract_to_file(self, countries_req: list, overwrite: bool = False) -> None
            Extracts the data associated with each country on the list and saves it into a (new) CSV file.

        visualize(self, countries_req: list) -> None
            Plots the data associated with the countries from the list. Displays an interactive plot.

        analyze_year(self, year: int) -> None
            Finds and displays the countries with the min and max emission levels in a year, and the year's average.

        verify_structure(self) -> bool
            Checks whether the data in the initialized dictionary is of the expected types.
    """

    @staticmethod
    def get_file(prompt: str) -> str:
        """
        Prompts the user to enter a CSV filename, checks if a non-empty file like that exists, and returns its name.

        Args:
            prompt (str): A message to display to the user.

        Returns:
            str: The name of a non-empty CSV file.
        """

        while True:
            user_inp = input(prompt)

            # If user's input doesn't include the ".csv" extension, append it.
            if not user_inp.lower().endswith(".csv"):
                user_inp += ".csv"

            try:
                # Try to open the file. If it exists, save the number of rows in it into a variable.
                with open(user_inp, newline="") as csvfile:
                    reader_len = len(list(csv.reader(csvfile)))
            except FileNotFoundError:
                print(f"There is no such file as: {user_inp}. Try again.")
                continue

            if reader_len < 2:
                print("The file must have at least two rows of data. Try again.")
                continue

            return user_inp

    def __init__(self, filename: str) -> None:
        """
        Initialize an object with the filename, data_dict, countries, first_key and first_value attributes.

        Args:
            filename (str): The name of a non-empty CSV file.

        Returns:
            None
        """

        self.filename = filename
        with open(filename, newline="") as csvfile:
            reader = csv.reader(csvfile)

            # Import the data from the file into a dictionary attribute.
            # The first element of each row is the key; the rest is the value.
            self.data_dict = {row.pop(0): row for row in reader}

        # Get a list of the keys (countries) from the dictionary.
        self.countries = list(self.data_dict.keys())

        # Get the first item from the list and the first value from the dictionary.
        self.first_key = self.countries.pop(0)
        self.first_value = self.data_dict.get(self.first_key)

        print("All the data has been read into a dictionary.\n")

    def get_year(self, prompt: str) -> int:
        """
        Prompts the user to enter a year in the range of self.first_value, inclusive. Returns the year.

        Args:
            prompt (str): A message to display to the user.

        Returns:
            int: The year entered by the user.
        """

        while True:
            user_inp = input(prompt)

            try:
                # Try to cast the user's input into an integer.
                user_inp = int(user_inp)
            except ValueError:
                print("You have not provided a year integer. Try again.")
                continue

            # Check whether the provided year is within the range of years in self.first_value.
            # This is done under the assumption the elements in that attribute are sorted.
            if not int(self.first_value[0]) <= user_inp <= int(self.first_value[-1]):
                print("You have provided an out-of-range year. Try again.")
                continue
            return user_inp

    def get_country(self, prompt: str, num: int, strict: bool = True) -> list[str]:
        """
        Prompts the user to enter a comma-separated string of countries, and returns their list if they are correct.

        Args:
            prompt (str): A message to display to the user.
            num (int): A number of countries to get.
            strict (bool): If True, expects exactly the num of countries; else, from 1 to num. Defaults to True.

        Returns:
            list[str]: The list of countries.
        """

        while True:
            user_inp = input(prompt).split(",")
            user_inp_len = len(user_inp)

            # Check if the length of the above list is as demanded by the num and strict arguments.
            if (strict and user_inp_len == num) or (not strict and 0 < user_inp_len <= num):
                # Strip each item in the list of whitespace on each side and capitalize each word in the item.
                # Also, lower the case of some words if they exists in the item.
                user_inp = [c.strip().title().replace(" And ", " and ").replace("D'", "d'")
                            for c in user_inp]

                # Check for any duplicates using a set.
                if len(set(user_inp)) < user_inp_len:
                    print("You have entered some duplicate countries. Try again.")
                    continue

                # Check whether all the items in the list correspond are found in self.countries.
                if not all([c in self.countries for c in user_inp]):
                    print("You have provided some incorrect names of countries. Try again.")
                    continue

                return user_inp
            print(f"The provided input is unexpected (you must enter {('from 1 to ', 'exactly')[strict]} {num}"
                  f" of countries). Try again.")

    def extract_to_file(self, countries_req: list, overwrite: bool = False) -> None:
        """
        Extracts the data associated with each country on the list and saves it into a (new) CSV file.

        Args:
            countries_req (list): A list of countries to extract.
            overwrite (bool): Whether to overwrite the [filename]_subset.csv file. Defaults to False.

        Returns:
            None
        """

        # Prepare the name for the subset by appending '_subset.csv' to the original CSV filename.
        subset_filename = self.filename.replace(".csv", "_subset.csv")

        # If the overwrite argument is False and the file already exist, incrementally find the closest free name.
        if not overwrite and exists(subset_filename):
            counter = 0
            name, ext = splitext(subset_filename)
            while exists(subset_filename):
                counter += 1
                subset_filename = f"{name}_{counter}{ext}"

        with open(subset_filename, "w+", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Write in the first row (the same for every possible extraction).
            writer.writerow([self.first_key] + self.data_dict[self.first_key])

            # For each country, write in a concatenation of two lists: the country's name, and the corresponding value.
            for c in countries_req:
                writer.writerow([c] + self.data_dict[c])

        print(f"\nData successfully extracted for {', '.join(countries_req)} and saved into the file: "
              f"{subset_filename}.")

    def visualize(self, countries_req: list) -> None:
        """
        Plots the data associated with the countries from the list. Displays an interactive plot.

        Args:
            countries_req (list): A list of countries to visualize.

        Returns:
            None
        """

        # Convert the first value of the data dictionary to a NumPy array.
        x_array = np.array(self.data_dict[self.first_key])

        # Create a list of even years to use as x-axis ticks.
        x_ticks = [year for year in self.data_dict[self.first_key] if not int(year) % 2]

        # Loop through the requested countries and plot their emissions data.
        for c in countries_req:
            plt.plot(x_array, np.array([float(k) for k in self.data_dict[c]]), label=c)

        # Get the current axes object.
        ax = plt.gca()

        # Format the y-axis labels to show two decimal places.
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

        # Set the x-axis ticks to the even years.
        ax.set_xticks(x_ticks)

        # Set the title of the plot.
        plt.title("Year vs Emissions in Capita")

        # Set the x-axis label.
        plt.xlabel("Year")

        # Set the y-axis label depending on the number of countries.
        plt.ylabel(f"Emissions in {', '.join(countries_req)}")
        if len(countries_req) > 1:
            # Add a legend to show the countries' names.
            ax.legend()

        # Show the plot.
        plt.show()

    def analyze_year(self, year: int) -> None:
        """
        Finds and displays the countries with the min and max emission levels in a year, and the year's average.

        Args:
            year (int): A year to analyze.

        Returns:
            None
        """

        # Get the provided year's index in self.data_dict.
        year_index = self.data_dict[self.first_key].index(str(year))

        # Cast all the data associated with that year into float, except for the first key-value pair of self.data_dict.
        year_values = [float(self.data_dict[k][year_index]) for k in self.data_dict if k != self.first_key]

        # Print the results of the following operations:
        # Find the indices of min & max values in year_values and get the corresponding countries in self.countries.
        # Calculate the annual average rounded to six decimal places.
        print(f"In {year}, countries with minimum and maximum CO2 emission levels were: "
              f"[{self.countries[year_values.index(min(year_values))]}] "
              f"and [{self.countries[year_values.index(max(year_values))]}], respectively.\n"
              f"Average CO2 emissions in {year} were {round(sum(year_values) / len(year_values), 6)}")

    def verify_structure(self) -> bool:
        """
        Checks whether the data in the initialized dictionary is of the expected types.

        Returns:
            bool
        """

        # Enumerate the items in the dictionary to have an easier way of tracking the index.
        enum_dict = enumerate(self.data_dict.items())
        for i, e in enum_dict:

            # Check if the first row's values can be cast into integers.
            if i == 0:
                try:
                    _ = [int(item) for item in e[1]]
                except ValueError:
                    return False

            else:
                # Check if the key has any letters, but omit any dashes or spaces.
                # The first column in the first row is of no consequence to the script, so such a check is omitted.
                if not e[0].translate(str.maketrans("", "", "-' ")).isalpha():
                    return False

                # Check if the other rows' values can be cast into floats.
                try:
                    _ = [float(item) for item in e[1]]
                except ValueError:
                    return False
        return True


def main():
    csv_obj = AnalysisCSV(AnalysisCSV.get_file("Provide the name of the file CSV you wish to read data from: "))

    # print(f"Is the file structured as expected? {('No', 'Yes')[csv_obj.verify_structure()]}.")
    csv_obj.analyze_year(csv_obj.get_year(f"Select a year to find statistics "
                                          f"({csv_obj.first_value[0]}-{csv_obj.first_value[-1]}): "))
    csv_obj.visualize(csv_obj.get_country("Select a country to visualize: ", 1))
    csv_obj.visualize(csv_obj.get_country("Select two comma-separated countries for which you want "
                                          "to visualize data: ", 2))
    csv_obj.extract_to_file(csv_obj.get_country("Select up to three comma-separated countries for you want "
                                                "to extract data: ", 3, False))


if __name__ == "__main__":
    main()
