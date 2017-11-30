/**
 * Created by Arthur on 11/30/2017.
 */
var ctx = document.getElementById('balInterest').getContext('2d');
new Chart(ctx, {
    // The type of chart we want to create
    type: 'line',
    // The data for our dataset
    data: {
        labels: ["January","February","March","April","May","June"],
        datasets: [
            {
                label: 'Balance',
                    // backgroundColor: 'rgb(0,42,84)',
                borderColor: 'rgb(0,42,84)',
                data: [30000, 25000, 42000, 55000, 52000, 54000],
                type: 'line'
            },
            {
                label: 'Interest',
                    // backgroundColor: 'rgb(0,42,84)',
                borderColor: 'rgb(206,32,32)',
                data: [31000, 26500, 44200, 57230, 54240, 56400]
            }
        ]
    },
    // Configuration options go here
    options: {}
});