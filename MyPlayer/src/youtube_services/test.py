# Count the number of letters to write all the 
# number from 1 to 1000.

basic_numbers = {0: "",
                 1: "one",
                 2: "two",
                 3: "three",
                 4: "four",
                 5: "five",
                 6: "six",
                 7: "seven",
                 8: "eight",
                 9: "nine",
                 10:"ten",
                 11: "eleven",
                 12: "twelve",
                 13: "thirteen",
                 14: "fourteen",
                 15: "fifteen",
                 16: "sixteen",
                 17: "seventeen",
                 18: "eighteen",
                 19: "nineteen",
                 20: "twenty",
                 30: "thirty",
                 40: "forty",
                 50: "fifty",
                 60: "sixty",
                 70: "seventy",
                 80: "eighty",
                 90: "ninety",
                 1000: "onethousand"}

# Get the number of letters needed to write a number.
def get_letter_number(n):
    if n in basic_numbers.keys():
        print basic_numbers[n]
        return len(basic_numbers[n])
    
    hundreds = n / 100
    n %= 100
    
    s = ""    
    count = 0
    if hundreds > 0:
        s = s + basic_numbers[hundreds] + " hundred"
        count = count + len("hundred") + len(basic_numbers[hundreds])
        if n > 0:
            s += ' and '
            count += len("and")
    if n in basic_numbers.keys():
        s += basic_numbers[n]
        count += len(basic_numbers[n])
    else:
        tens = n / 10 * 10
        s += basic_numbers[tens] + " "
        count += len(basic_numbers[tens])    
        units = n % 10
        s += basic_numbers[units]
        count += len(basic_numbers[units])
        
    print s
        
    return count
        
count = 0        
for i in range(1, 1000 + 1):
    #print "%d : %d" %(i, get_letter_number(i))
    count += get_letter_number(i)
print "Final result: %d"% count    
    
    