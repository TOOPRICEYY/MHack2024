
  const chatWindow = document.getElementById('chatWindow');

  function expandChat() {
    chatWindow.classList.remove('translate-y-[calc(-100%+70px)]');
    chatWindow.classList.remove('hover:translate-y-[calc(-100%+75px)]');
  }
  
  // This function contracts the chat window
  function contractChat() {
    chatWindow.classList.add('translate-y-[calc(-100%+70px)]');
    chatWindow.classList.add('hover:translate-y-[calc(-100%+75px)]');

  }
let chatEle = document.getElementById("chatInput");
chatEle.addEventListener('focus',  ()=>{
    expandChat();
});
chatEle.addEventListener('blur',  ()=>{
    contractChat();
});

// Assuming you're including Chart.js in your content script
// console.log(ctx)
var liveGraph = null
var liveRadar = null

dataStreamCategories = ["Tension","Excitement","Professionalism","Solumn"]

try{
setTimeout(()=>{
    const liveGraphctx = document.getElementById('liveLine').getContext('2d');

    liveGraph = new Chart(liveGraphctx, {
        type: 'line',
        data: {
          labels: [], // Initialize empty labels array
          datasets: dataStreamCategories.map(category => ({
            label: category,
            data: [],
            fill: false,
            borderColor: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`,
            lineTension: 0.4,
            borderWidth: 2
          }))
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
           
            x: {
              display: true,
              title: {
                display: false
              },
              ticks: {
                autoSkip: true,
                maxTicksLimit: 4 // Limit the number of x-axis labels to avoid clutter
              }
            },
            
            y: {
            beginAtZero: true,
            ticks: {
                min:-0.1,
                max:1.1,
            // Map the numeric value to qualitative descriptors
            callback: function(value, index, values) {
                if (value === 0) return 'Low';
                if (value === 0.5) return 'Medium';
                if (value === 1) return 'High';
            }
            },
            // afterBuildTicks: function(axis) {
            // // Manually define the ticks for the y-axis
            // axis.ticks = [0, 0.5, 1];
            // },
              display: true,
              title: {
                display: false
              },
              grid: {
                drawBorder: false,
                color: function(context) {
                  if (context.tick.value === 0) {
                     return 'rgba(0, 0, 0, 0)'; // Make the zero line stronger
                  } else {
                     return 'rgba(0, 0, 0, 0.05)'; // Soften the grid lines
                  }
                }
              }
            }
          },
          plugins: {
            legend: {
              display: true, // Display the legend
              position: 'top', // Position the legend at the top
              labels: {
                usePointStyle: true // Use point style for a better aesthetic
              }
            },
            tooltip: {
              enabled: true, // Enable tooltips
              mode: 'index',
              position: 'nearest',
              backgroundColor: 'rgba(255, 255, 255, 0.8)', // Tooltip with slight transparency
              titleColor: '#000', // Title color
              bodyColor: '#000', // Body color
              borderColor: 'rgba(0, 0, 0, 0.1)', // Border color
              borderWidth: 1 // Border width
            }
          },
          elements: {
            point: {
              radius: 1 // Small radius for points to be visible but not intrusive
            },
            line: {
              tension: 0.3 // Reducing tension to make the line a bit less curved
            }
          },
          interaction: {
            intersect: false,
            mode: 'nearest'
          },
          animation: {
            duration: 750, // Animation duration of 750ms for smoother transitions
            easing: 'easeInOutQuart' // Easing function for a more dynamic effect
          }
        }
      });
      const liveRadarctx = document.getElementById('liveRadar').getContext('2d');

      liveRadar = new Chart(liveRadarctx, {
        type: 'radar',
        data: {
          labels: dataStreamCategories, // Initialize empty labels array
          datasets: [{
            label: 'Live Data',
            data: [], // Initialize empty data array
            backgroundColor: 'rgba(75,192,192,0.4)', // Semi-transparent teal
            borderColor: 'rgba(75,192,192,1)', // Solid teal border
          }]
        },
        options: {
          scale: {
            ticks: {
              beginAtZero: true,
              min: 0, // Set minimum value
              max: 1, // Set maximum value
              stepSize: 0.25, // Define the step size between ticks
              // Custom label formatting
              callback: function(value, index, values) {
                if (value === 0) return 'Low';
                if (value === 0.5) return 'Med';
                if (value === 1) return 'High';
              }
            },
            pointLabels: {
              fontSize: 14 // Adjust the font size of the point labels if necessary
            }
          },
          elements: {
            line: {
              tension: 0.4 // Makes lines smoother
            }
          },
          plugins: {
            legend: {
                // position: 'bottom',
                display: false
            },
          },
          // legend: {
          //   position: 'bottom', // Legend at the top
          //   display:false
          // },
          responsive: false, // Makes the chart responsive
          maintainAspectRatio: false // Ensures that aspect ratio is not maintained
        }
      });
      // liveRadar = new Chart(liveRadarctx, {
      //   type: 'radar',
      //   data: {
      //     labels: dataStreamCategories,
      //     datasets: [{
      //       label: 'Current Data',
      //       data: [],
      //       fill: true,
      //       backgroundColor: 'rgba(75,192,192,0.4)',
      //       borderColor: 'rgba(75,192,192,1)'
      //     }, {
      //       label: 'My Second Dataset',
      //       data: [28, 48, 40, 19, 96, 27, 100],
      //       fill: true,
      //       backgroundColor: 'rgba(54, 162, 235, 0.2)',
      //       borderColor: 'rgb(54, 162, 235)',
      //       pointBackgroundColor: 'rgb(54, 162, 235)',
      //       pointBorderColor: '#fff',
      //       pointHoverBackgroundColor: '#fff',
      //       pointHoverBorderColor: 'rgb(54, 162, 235)'
      //     }]
      //   },
        
      //   options: {
      //     legend: {
      //       // display: false,
      //       position: 'bottom',
      //       // labels: {
      //       //   font: {
      //       //     size: 2 // Adjust the font size here to make the legend smaller
      //       //   },
      //       //   padding: 2 // Adjust padding around text to reduce the space
      //       // }
      //     },
      //     elements: {
      //       line: {
      //         borderWidth: 3
      //       }
      //     },
      //     scale: {
      //       ticks: {
      //         beginAtZero: true
      //       }
      //     },
      //     responsive: true,
      //     maintainAspectRatio: true
      //   }
      // });
      
      
console.log(liveRadar)

},100);
}catch (e){
    console.log(e);

}



function updateGraph(newData) {
    const data = liveGraph.data;
    console.log(data)
    
    // Assuming newData is an object like {label: '1s', value: 20}
    data.labels.push(newData.label);
    data.datasets.forEach((dataset) => {
      dataset.data.push(newData.value);
    });
    
    liveGraph.update();
  }
  

//   // Example: Update the graph every second with random data for demonstration
//   setInterval(() => {
//     const randomValue = Math.floor(Math.random() * 100);
//     const currentTime = int(new Date().toUTCString);
//     updateGraph({ label: currentTime, value: randomValue });
//   }, 1000);
  
function getCurrentTime() {
    const now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();

    // Adding leading zeros if the number is less than 10
    hours = hours < 10 ? '0' + hours : hours;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    seconds = now.getSeconds();

    return `${hours}:${minutes}:${seconds}`;
}

console.log(getCurrentTime()); // Outputs time in HH:MM format

function addData(chart, label,data, streamIndex) {

    // console.log(chart.data.datasets.find(x=>x.label===streamIndex))

    if(!chart.data.labels.includes(label)) chart.data.labels.push(label); // Push the new label
    chart.data.datasets.find(x=>x.label===streamIndex).data.push(data); // Push new data to specific stream

    chart.update();
  }

  setInterval(() => {
try{
    const randomValue = Math.floor(Math.random()*10)/10.0;
    const randomValue2 = Math.floor(Math.random()*10)/10.0;

    const currentTime = getCurrentTime();
    // updateGraph({ label: currentTime, value: randomValue });
    addData(liveGraph,currentTime,randomValue,"Tension")
    addData(liveGraph,currentTime,randomValue2,"Excitement")

}catch (e){
    console.log(e);

}
  }, 1000);
async function pollForDataBatch() {
  const currentTime = getCurrentTime(); // Get the current time for labels
  // const newValues = dataStreamCategories.map(() => Math.random()); // Generate random values for each category
  try {
      const response = await fetch('http://127.0.0.1:5001/get_state_data', {
          method: 'GET',
          headers: {
              'Content-Type': 'application/json'
          },
          // body: JSON.stringify({ message:message}) // Example body
      });

      const data = await response.json();
      if(data.status = "404") {
        console.log("no new data")
        return

      }
      console.log(data)
  } catch (error) {
      console.error('Error:', error);
      return;
  }


  // Update line chart
  if (liveGraph) {
    liveGraph.data.labels.push(currentTime); // Add the current time as a new label
    liveGraph.data.datasets.forEach((dataset, index) => {
      dataset.data.push(newValues[index]); // Push new values to each dataset
    });
    liveGraph.update();
  }

  // Update radar chart with only the latest values
  if (liveRadar) {
    liveRadar.data.datasets.forEach((dataset, index) => {
      dataset.data = newValues; // Update the entire data array with new values
    });
    liveRadar.update();
  }
}

// Update charts every second with new data
// setInterval(pollForDataBatch, 1000);




  // Send message on Enter
  const chatInput = document.getElementById('chatInput');
  chatInput.addEventListener('keypress', function (event) {
      if (event.key === 'Enter') {
          sendMessage();
      }
  });
  function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
// async function sleep(fn, ...args) {
//     await timeout(3000);
//     return fn(...args);
// }
  // SendMessage function
  async function sendMessage() {
    const input = chatInput;
    const loading = document.getElementById('loading');
    if (document.activeElement === input && input.value.trim() !== '') {
        const message = input.value;
        addMessage(message, 'right');
        input.value = '';
        loading.classList.remove('hidden'); // Show loading

        // await timeout(3000)

        try {
            const response = await fetch('http://127.0.0.1:5001/send_text_prompt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message:message}) // Example body
            });

            const data = await response.json();
            addMessage(data.response, 'left');
        } catch (error) {
            console.error('Error:', error);
            addMessage('Failed to send message.', 'left');
        }

        loading.classList.add('hidden'); // Hide loading
    }
}


function addMessage(text, side) {
  const container = document.getElementById('messageContainer');
  const messageDiv = document.createElement('div');
  messageDiv.className = `mb-4 p-2 bg-gray-100 rounded ${side === 'left' ? 'text-right' : ''}`;
  messageDiv.textContent = text;
  container.appendChild(messageDiv);
  container.scrollTop = container.scrollHeight; // Auto-scroll to the latest message
}


