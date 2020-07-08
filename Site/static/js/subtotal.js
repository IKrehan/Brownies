$(document).ready(function(){
    $('.price').each(function() {
        calculateSum();
    });
    });
    
     function calculateSum() {
    
    var sum = 0;
    //iterate through each td based on class and add the values
        $(".price").each(function() {
    
            var value = $(this).text();
            //add only if the value is number
            if(!isNaN(value) && value.length!=0) {
                sum += parseFloat(value);
            }
    
        });
    $('#result').text(sum);    
    };