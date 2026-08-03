pragma circom 2.0.0;
include "node_modules/circomlib/circuits/comparators.circom";

template AgeCheck() {
    signal input current_year;
    signal input birth_year;
    signal input age_threshold;

    component geq = GreaterEqThan(8); 
    
    geq.in[0] <== current_year - birth_year;
    geq.in[1] <== age_threshold;

    geq.out === 1;
}

component main {public [current_year, age_threshold]} = AgeCheck();