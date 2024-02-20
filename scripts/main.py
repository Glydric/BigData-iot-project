import pandas as pd
from getDataset import getAvailableMachines, getEntireDataset
from plots import plot

if __name__ == "__main__":
    pd.set_option("display.max_rows", None)
    pd.options.mode.copy_on_write = True

    try:
        machines = getAvailableMachines()
        dfs = []
        errors = []
        # try:
        #     print(getEntireDataset(306, 2022, 7))
        # except Exception as e:
        #     errors.append(e)
        plot(getEntireDataset(306, 2023, 1))

        for machineId in machines:
            for year in machines[machineId].keys():
                for month in machines[machineId][year]:
                    print(
                        f"\n\n----- Machine {machineId} Year {year} Month {month} ------"
                    )
                    try:
                        df = getEntireDataset(machineId, year, month)
                        plot(df, machineId)

                        df["ID"] = machineId
                        dfs.append(df)
                    except Exception as e:
                        print(f"Error {e}")
                        errors.append(e)
                        errors.append(
                            {
                                "machineId": machineId,
                                "year": year,
                                "month": month,
                                "error": e,
                            }
                        )

        if errors != []:
            print(errors)
        completeDataset = pd.concat(dfs, ignore_index=True)

        print(f"\n----- Entire Dataset {id} ------\n")

        print(completeDataset)
        print(completeDataset.shape)
        plot(completeDataset)

    except Exception as e:
        print(e)
