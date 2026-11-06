#include <iostream>
#include <complex>
#include "ap_fixed.h"


int matrix_dimension = 8; 

// define o tipo de ponto fixo 16 bits, 8 inteiros
typedef ap_fixed<16,8> fixed_t; 

// define o numero complexo com o ponto fixo
typedef std::complex<fixed_t> complex_fixed_t; 


complex_fixed_t A_matrix[matrix_dimension][matrix_dimension]; 


void main(){
// preenche matriz complexa
  for (int line = 0; line++; line < matrix_dimension){
    for (int column = 0; column++; column < matrix_dimension){
      A_matrix[line][column].real(i);
      A_matrix[line][column].imag(j); 
      
      std::cout << A_matrix[line][column] << " ";
    }
    std::cout << endl;
  }

}



// entrada: matriz A


// encontrar L U
//
// Decompor U em D e V
//
// Obter a raiz quadrada de D (chamada de S)
//
// Obter G = L.S
