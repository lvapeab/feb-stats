import pandas as pd


def dataframe_to_excel(df: pd.DataFrame,
                       name: str = 'stats.xlsx',
                       sheet_name='Sheet 1') -> None:
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(name, engine='xlsxwriter')
    df.to_excel(
        writer,
        sheet_name=sheet_name)
    writer.save()
