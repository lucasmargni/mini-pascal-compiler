from syntactic_analyzer import SyntacticAnalyzer
import sys

# parameter: name of the input file
if(len(sys.argv) < 2):
    print("Error: it is required the name of the input file as parameter")
    sys.exit(1)

# pascal file recived
input_file : str = sys.argv[1]

syntactic : SyntacticAnalyzer = SyntacticAnalyzer(input_file)
syntactic.main()

print("Pascal program processed successfully!")
print("No syntax errors found. The program conforms to the grammar.")