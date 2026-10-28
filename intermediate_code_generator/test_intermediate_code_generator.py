from intermediate_code_generator import IntermediateCodeGenerator
import sys
import os

# parameter: name of the input file
if(len(sys.argv) < 2):
    print("Error: it is required the name of the input file as parameter")
    sys.exit(1)

# pascal file recived
input_file : str = sys.argv[1]

OUTPUT_DIR = "mepa_output"

file_name = os.path.splitext(os.path.basename(input_file))[0] + ".mep"
output_file = os.path.join(OUTPUT_DIR, file_name)
# test_cases/test_case1.pas --> mepa_output/test_case1.mep

# se crea la carpeta si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

generator = IntermediateCodeGenerator(input_file)
generator.main()
generator.write_output(output_file)

print(f"MEPA code generated in '{output_file}'")