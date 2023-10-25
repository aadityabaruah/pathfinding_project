let isVisualizing = false;

document.addEventListener("DOMContentLoaded", function() {
    const gridContainer = document.getElementById("grid-container");
    const startBtn = document.getElementById("start-btn");
    const resetBtn = document.getElementById("reset-btn");

    let isPickupMode = false;

    const pickupBtn = document.getElementById("pickup-btn");

    pickupBtn.addEventListener("click", function() {
        isPickupMode = !isPickupMode;  // Toggle the mode
        if (isPickupMode) {
            this.textContent = "Cancel Pickup Point Placement";
        } else {
            this.textContent = "Toggle Pickup Point Placement";
        }
    });

    // Generate the grid
    for (let i = 0; i < 2500; i++) { // Example: 50x50 grid
        const cell = document.createElement("div");
        cell.classList.add("cell");
        cell.dataset.id = i;
        gridContainer.appendChild(cell);
    }

    // Event listeners for start, target, and walls
    let isDrawing = false;
    gridContainer.addEventListener("mousedown", function(event) {
        if (event.target.classList.contains("cell")) {
            isDrawing = true;
            if (!document.querySelector(".cell.start")) {
                event.target.classList.add("start");
            } else if (!document.querySelector(".cell.target")) {
                event.target.classList.add("target");
            } else if (isPickupMode && !document.querySelector(".cell.pickup")) {
                event.target.classList.add("pickup");
                isPickupMode = false;  // Reset the mode after placing the pickup point
                pickupBtn.textContent = "Toggle Pickup Point Placement";  // Update the button text
            } else {
                event.target.classList.add("wall");
            }
        }
    });




    gridContainer.addEventListener("mousemove", function(event) {
        if (isDrawing && document.querySelector(".cell.start") && document.querySelector(".cell.target")) {
            event.target.classList.add("wall");
        }
    });

    document.addEventListener("mouseup", function() {
        isDrawing = false;
    });

    // AJAX call to compute path
    startBtn.addEventListener("click", function() {
        const cells = document.querySelectorAll(".cell");
        let gridData = Array.from(cells).map(cell => {
            return {
                isWall: cell.classList.contains("wall"),
                isStart: cell.classList.contains("start"),
                isTarget: cell.classList.contains("target"),
                isPickup: cell.classList.contains("pickup"),  // Include this line for pickup point
                id: parseInt(cell.dataset.id)
            };
        });



        let selectedAlgorithm = document.getElementById("algorithm-select").value;

        fetch("/compute_path/", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                grid: gridData,
                algorithm: selectedAlgorithm
            })
        })
        .then(response => response.json())
        .then(data => {
            visualizeAlgorithm(data);
        });
    });

    // Reset the grid
    resetBtn.addEventListener("click", function() {
        isVisualizing = false;
        const cells = document.querySelectorAll(".cell");
        cells.forEach(cell => {
            cell.className = "cell"; // This resets all classes on the cell
            cell.style.backgroundColor = ""; // This resets any inline styles applied
        });
    });


    // Visualize algorithm's progress
    function visualizeAlgorithm(data) {
        isVisualizing = true;
        let visitedCells = data.visited_cells;
        let finalPath = data.final_path;
        let delay = 15;  // Reduced for faster visualization

        for (let i = 0; i < visitedCells.length; i++) {
        setTimeout(function() {
            if (!isVisualizing) return; // Exit if visualization is stopped
            let cell = document.querySelector(`[data-id="${visitedCells[i]}"]`);

            // Check if the cell is start, target, or pickup, and if so, skip coloring it
            if (cell.classList.contains("start") || cell.classList.contains("target") || cell.classList.contains("pickup")) {
                return;
            }

            cell.style.backgroundColor = "yellow";
        }, i * delay);
    }

        setTimeout(function() {
            if (!isVisualizing) return;
            let delayPath = 50; // Adjust for desired speed
            for(let i = 0; i < finalPath.length; i++) {
                setTimeout(function() {
                    let cellId = finalPath[i];
                    let cell = document.querySelector(`[data-id="${cellId}"]`);
                    if (cell.classList.contains("start") || cell.classList.contains("target")) {
                        return;
                    }
                    cell.style.backgroundColor = "blue";
                }, i * delayPath);
            }
        }, visitedCells.length * delay);
    }


    // Get Django CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
