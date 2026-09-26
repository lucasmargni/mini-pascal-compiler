from syntactic_semantic_analyzer import SyntacticSemanticAnalyzer
import sys

# parameter: name of the input file
if(len(sys.argv) < 2):
    print("Error: it is required the name of the input file as parameter")
    sys.exit(1)

# pascal file recived
input_file : str = sys.argv[1]

syntactic_semantic : SyntacticSemanticAnalyzer = SyntacticSemanticAnalyzer(input_file)
syntactic_semantic.main()

print("Pascal program processed successfully!")
print("No syntax nor semantic errors found. The program conforms to the grammar and restriction types.")