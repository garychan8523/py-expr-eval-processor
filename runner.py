import json
import yaml

from common import functions
from libs import ast

class Processor:
    def __init__(self, data_file):
        self.context = {
            'temp': {},
            'data': {},
            'configs': []
        }

        # load data
        self.context['data'] = json.load(open(data_file))

        # load config
        for processor in self.context['data']['processors']:
            with open(processor, 'r') as stream:
                try:
                    self.context['configs'].append(yaml.safe_load(stream))
                except yaml.YAMLError as ex:
                    print(ex)
    
    
    def process_instructions(self, section, portfolio_index=-1, position_index=-1, **kwargs):
        print(f'process_instructions({section}, {kwargs})')
        if section is None:
            return
        variables = {
            'processor': self,
            'portfolio_index': portfolio_index,
            'position_index': position_index
        }
        for formulas in section:
            for variable in formulas:
                expr = str(formulas[variable])
                print(f'expr {expr}')
                if variable == 'exec':
                    _output = ast.literal_eval(expr, variables, functions)
                    print(f'exec output - values {_output} {type(_output)}')
                else:
                    self.context['temp'][variable] = ast.literal_eval(expr, variables, functions)
    

    def process(self):
        for config in self.context['configs']:
            # preprocessing
            self.process_instructions(config['preprocessing'])

            # processing
            for i, portfolio in enumerate(self.context['data']['portfolios']):
                for j, position in enumerate(portfolio['positions']):
                    self.process_instructions(config['position'], portfolio_index=i, position_index=j)
                self.process_instructions(config['portfolio'], portfolio_index=i, position_index=j)

            # postprocessing
            self.process_instructions(config['postprocessing'])


def main():
    Processor('data.json').process()


if __name__ == '__main__':
    main()

