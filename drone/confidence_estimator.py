from pathlib import Path
import pandas as pd


class CE:

    def __init__(self):
        self.price_profile = None
        self.scheduler = Scheduler()

    def load_price_data(self, csv_file_path: Path):
        price_data = pd.read_csv(csv_file_path, sep=',', parse_dates=True, index_col='date')
        price_data = price_data.interpolate(method='linear')  # interpolate NaN values
        price_data.index = pd.to_datetime(price_data.index, format="%d.%m.%Y %H:%M")
        price_data = price_data.squeeze(axis=0)
        self.price_profile = price_data

    def get_price_data(self):
        return self.price_profile

    def check_constraints_with_scheduler(self):
        schedule = self.scheduler.generate_schedule()

    def delete_most_expensive_slot(self, charging_constraint: pd.Series):
        pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ROOT_DIR = Path().resolve()
    my_CE = CE()
    my_CE.get_price_data(csv_file_path = ROOT_DIR / 'data' / 'price_profiles' / 'prices2012-2023.csv')
    print(my_CE.get_price_profile)

