// Get the form element and other necessary DOM elements
const parseForm = document.getElementById('parse');
const searchForm = document.getElementById('search');
const deleteForm = document.getElementById('deleteForm');
const scoreDiv = document.getElementById('score');
const loadingSpinner = document.getElementById('loading-spinner');
const CX_LOGO = document.getElementById('CX_LOGO');
const file_border = document.getElementsByClassName("selected-file-name");
const selectAllCheckbox = document.getElementById('select_all');


// Function to submit the score form
function submitScoreForm() {
    const formData = new FormData(searchForm); // Get the form data

    fetch('/score', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(results => {
            // Handle and display the results as needed
            const scoreTable = document.getElementById('scoreTable');
            scoreTable.innerHTML = ''; // Clear any previous content from the score table

            // Sort results based on score in descending order
            results.sort((a, b) => b[1] - a[1]);

            // Populate the score table with the sorted results
            for (const result of results) {
                const filename = result[0];
                const score = result[1];
                const keywords = result[2];

                const row = document.createElement('tr');
                const deleteCell = document.createElement('td'); // Create delete cell
                const fileNameCell = document.createElement('td');
                const scoreCell = document.createElement('td');
                const keywordsCell = createKeywordsField(keywords);

                deleteCell.appendChild(createDeleteButton(filename)); // Add delete button to delete cell

                fileNameCell.textContent = filename;
                scoreCell.textContent = `${score}%`;

                row.appendChild(deleteCell); // Add delete cell to the row
                row.appendChild(fileNameCell);
                row.appendChild(scoreCell);
                row.appendChild(keywordsCell);

                scoreTable.appendChild(row);
            }


            // Show the score section after getting results
            scoreDiv.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Function to create a delete button for each row
function createDeleteButton(filename) {
    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete';
    deleteButton.addEventListener('click', () => {
        deleteRow(filename);
    });
    return deleteButton;
}

// Function to create a clickable keywords field for each row
function createKeywordsField(keywords) {
    const keywordsField = document.createElement('td');
    keywordsField.classList.add('keywords-cell');

    // Create a list element to hold each keyword in a separate list item
    const keywordsList = document.createElement('ul');
    keywordsList.classList.add('keywords-list');

    // Add each keyword as a list item
    for (const keyword of keywords) {
        const keywordItem = document.createElement('li');
        keywordItem.textContent = keyword;
        keywordsList.appendChild(keywordItem);
    }

    // Set initial visibility of keywords list to hidden
    keywordsList.style.display = 'none';

    // Show "View Keywords" text initially
    const viewKeywordsText = document.createElement('div');
    viewKeywordsText.textContent = "View Keywords";
    keywordsField.appendChild(viewKeywordsText);

    // Add click event listener to toggle keywords list visibility
    keywordsField.addEventListener('click', () => {
        if (keywordsList.style.display === 'block') {
            keywordsList.style.display = 'none'; // Hide the keywords list
            viewKeywordsText.style.display = 'block'; // Show "View Keywords" text
        } else {
            keywordsList.style.display = 'block'; // Show the keywords list
            viewKeywordsText.style.display = 'none'; // Hide "View Keywords" text
        }
    });

    keywordsField.appendChild(keywordsList);
    return keywordsField;
}

// Function to handle row deletion
function deleteRow(filename) {
    fetch('/delete_row', {
        method: 'POST',
        body: JSON.stringify({ filename: filename }), // Send filename to server
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                // Reload the score table after successful deletion
                submitScoreForm();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}


// Add event listener to role select
const roleSelect = document.getElementById('role1');
roleSelect.addEventListener('change', updateSearchWords);

// Function to show/hide div elements based on selected role
function showDivForRole(selectedRole) {
    // Hide all div elements
    const allDivs = document.querySelectorAll('.role-div');
    allDivs.forEach(div => {
        div.style.display = 'none';
    });

    // Show the selected role's div
    const selectedDiv = document.getElementById(selectedRole);
    if (selectedDiv) {
        selectedDiv.style.display = 'block';
    }
}

// Function to update search words based on selected role
function updateSearchWords() {
    const roleSelect = document.getElementById('role1');
    const selectedRole = roleSelect.value;
    
    // Show/hide divs based on selected role
    showDivForRole(selectedRole);
}

// Add event listener to the parse button
parseForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(parseForm); // Get the form data
    loadingSpinner.style.display = 'block'; // Show the loading spinner
    CX_LOGO.style.display = 'block'; // Show the loading spinner


    try {
        const response = await fetch('/parse', { // Send the form data to the server for processing
            method: 'POST',
            body: formData,
        });

        loadingSpinner.style.display = 'none'; // Hide the loading spinner after receiving the response
        CX_LOGO.style.display = 'none';

        if (!response.ok) {
            throw new Error(`Server returned an error. Status: ${response.status}`);
        }

        submitScoreForm();

    } catch (error) {
        console.error('Error:', error);
        const scoreDisplay = document.getElementById('scoreText');
        scoreDisplay.innerText = 'An error occurred. Please try again.';
    }
});

// Add event listener to the file input
const fileInput = document.getElementById('fileInput');
const selectedFileName = document.getElementById('selectedFileName');

fileInput.addEventListener('change', () => {
    // Update the selected file name
    if (fileInput.files.length > 0) {
        selectedFileName.textContent = fileInput.files[0].name;
        selectedFileName.style.display = 'inline';
    } else {
        selectedFileName.textContent = '';
        selectedFileName.style.display = 'none';
    }
});

// Add event listener to the form submit button
searchForm.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent default form submission
    submitScoreForm();
});

window.addEventListener('load', () => {
    // Trigger the "Load Scores" form submission when the page loads
    submitScoreForm();
});

// Add event listener to the "Select All" checkbox
selectAllCheckbox.addEventListener('change', () => {
    console.log("Select all checkbox change")
    const selectedRole = roleSelect.value;
    const selectedRoleDiv = document.getElementById(selectedRole);
    const generalRoleDiv = document.getElementById('General');

    // Unselect all checkboxes first
    const checkboxes = selectedRoleDiv.querySelectorAll('input[type="checkbox"][name="search_word"]');
    console.log(checkboxes)
    for (const checkbox of checkboxes) {
        checkbox.checked = false;
    }

    const generalCheckboxes = generalRoleDiv.querySelectorAll('input[type="checkbox"][name="search_word"]');
    console.log(generalCheckboxes)
    for (const checkbox of generalCheckboxes) {
        checkbox.checked = selectAllCheckbox.checked;
    }
    
    // For other roles, select visible keywords in the selected role's div
    for (const checkbox of checkboxes) {
        checkbox.checked = selectAllCheckbox.checked;
    }
});

// Call the function initially to populate search words based on the default role
updateSearchWords();

// Function for handling the Delete button state
const deleteButton = document.getElementById('deleteButton');
let deleteConfirmation = false; // Flag to track whether user confirmed deletion
let countdownInterval;

// Function to start the countdown for deletion confirmation
function startCountdown() {
    let countdown = 5; // Countdown in seconds
    deleteButton.style.color = 'red'; // Change text color to red
    deleteButton.value = `Are you sure? (${countdown})`;

    countdownInterval = setInterval(() => {
        countdown--;
        deleteButton.value = `Are you sure? (${countdown})`;

        if (countdown <= 0) {
            clearInterval(countdownInterval);
            deleteButton.value = 'Delete All Resumes';
            deleteButton.style.color = ''; // Reset text color
            deleteConfirmation = false;
        }
    }, 1000);
}

// Add click event listener to the "Delete All Resumes" button
deleteButton.addEventListener('click', () => {
    if (!deleteConfirmation) {
        // First click, start countdown for deletion confirmation
        deleteConfirmation = true;
        startCountdown();
    } else {
        // Second click, proceed with form submission
        clearInterval(countdownInterval); // Clear the countdown interval
        deleteButton.style.color = ''; // Reset text color
        deleteButton.textContent = 'Deleting...'; // Indicate deletion process

        const deleteForm = document.getElementById('deleteForm');
        deleteForm.submit(); // Submit the form
    }
});