from Token import Token
from LexicalAnalyzer import LexicalAnalyzer
from typing import List
import sys

# parameter: name of the input file
if(len(sys.argv) < 2):
    print("Error: it is required the name of the input file as parameter")
    sys.exit(1)

# pascal file recived
input_file : str = sys.argv[1]

# list of all tokens generated from the input file
token_list : List[Token] = []

lexical : LexicalAnalyzer = LexicalAnalyzer(input_file)
token_recived : Token | None = lexical.next_token()

while(token_recived):
    token_list.append(token_recived)
    token_recived = lexical.next_token()

output_file = open("result.out", "w")

for token in token_list:
    output_file.write(token.toString())
    output_file.write("\n")

print("Pascal program processed successfully!")
print("See all tokens in result.out")

output_file.close()