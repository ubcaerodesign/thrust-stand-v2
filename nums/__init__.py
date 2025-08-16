import pandas as pd

class Datasheet:
    def __init__(self, cols):
        self.dataframe = pd.DataFrame(columns=cols)

    def addPoint(self, data: dict):
        """
        data: dictionary of values each corresponding to a column in the dataframe
        """
        newRow = pd.DataFrame(data, index=[0])
        self.dataframe = pd.concat([self.dataframe, newRow], ignore_index=True)

        print(self.dataframe)

    def getDF(self) -> pd.DataFrame:
        return self.dataframe

    def export(self, filename):
        self.dataframe.to_excel(filename, index=False)