import math
class Helper():

    @staticmethod
    def organize_products(prod_list):
        return_list = [] 
        row_count = math.ceil(len(prod_list)/4)
        start = 0
        end = 4
        for num in range(row_count):
            return_list.append(prod_list[start:end])
            start = start + 4
            end = end + 4
        return return_list