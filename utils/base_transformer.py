import pyterrier as pt
import utils.repair_result_dataframe as rd
class ResultTransformer(pt.Transformer):
    def __init__(self,dataframe):
        super().__init__()
        self.dataframe = dataframe
        self.transform_own =  pt.Transformer.from_df(dataframe, uniform=True)

    def transform(self, input):

        result = self.transform_own.transform(input)
        return result

    def __mod__(self , right: int) :
        filtered_df = rd.cut_retrieval_results_top_n(self.dataframe, right)
        return filtered_df

    def __xor__(self, right : 'Transformer') -> 'Transformer':
        return self.transform_own ^ right
