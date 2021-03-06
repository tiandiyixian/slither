from slither.core.declarations.solidity_variables import (SolidityFunction,
                                                          SolidityVariableComposed)
from slither.detectors.abstract_detector import (AbstractDetector,
                                                 DetectorClassification)
from slither.slithir.operations import (HighLevelCall,
                                        LowLevelCall, 
                                        LibraryCall)
from slither.utils.code_complexity import compute_cyclomatic_complexity


class ComplexFunction(AbstractDetector):
    """
    Module detecting complex functions
        A complex function is defined by:
            - high cyclomatic complexity
            - numerous writes to state variables
            - numerous external calls
    """


    ARGUMENT = 'complex-function'
    HELP = 'Complex functions'
    IMPACT = DetectorClassification.INFORMATIONAL
    CONFIDENCE = DetectorClassification.MEDIUM

    MAX_STATE_VARIABLES = 10
    MAX_EXTERNAL_CALLS = 5
    MAX_CYCLOMATIC_COMPLEXITY = 7

    CAUSE_CYCLOMATIC = "cyclomatic"
    CAUSE_EXTERNAL_CALL = "external_calls"
    CAUSE_STATE_VARS = "state_vars"


    @staticmethod
    def detect_complex_func(func):        
        """Detect the cyclomatic complexity of the contract functions
           shouldn't be greater than 7
        """
        result = []
        code_complexity = compute_cyclomatic_complexity(func)

        if code_complexity > ComplexFunction.MAX_CYCLOMATIC_COMPLEXITY:
            result.append({
                "func": func,
                "cause": ComplexFunction.CAUSE_CYCLOMATIC
            })

        """Detect the number of external calls in the func
           shouldn't be greater than 5
        """
        count = 0
        for node in func.nodes:
            for ir in node.irs:
                if isinstance(ir, (HighLevelCall, LowLevelCall, LibraryCall)):
                    count += 1

        if count > ComplexFunction.MAX_EXTERNAL_CALLS:
            result.append({
                "func": func,
                "cause": ComplexFunction.CAUSE_EXTERNAL_CALL
            })
        
        """Checks the number of the state variables written
           shouldn't be greater than 10
        """
        if len(func.state_variables_written) > ComplexFunction.MAX_STATE_VARIABLES:
            result.append({
                "func": func,
                "cause": ComplexFunction.CAUSE_STATE_VARS
            })

        return result

    def detect_complex(self, contract):
        ret = []
        
        for func in contract.all_functions_called:
            result = self.detect_complex_func(func)
            ret.extend(result)

        return ret
    
    def detect(self):
        results = []

        for contract in self.contracts:
            issues = self.detect_complex(contract)

            for issue in issues:
                func, cause = issue.values()
                func_name = func.name
                
                txt = "Complex function in {} Contract: {}, Function: {}"

                if cause == self.CAUSE_EXTERNAL_CALL:
                    txt += ", Reason: High number of external calls"
                if cause == self.CAUSE_CYCLOMATIC:
                    txt += ", Reason: High number of branches"
                if cause == self.CAUSE_STATE_VARS:
                    txt += ", Reason: High number of modified state variables"

                info = txt.format(self.filename,
                                    contract.name,
                                    func_name)
                self.log(info)

                results.append({'vuln': 'ComplexFunc',
                                'sourceMapping': func.source_mapping,
                                'filename': self.filename,
                                'contract': contract.name,
                                'func': func_name})
        return results

