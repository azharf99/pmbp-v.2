let attendanceChartInstance;
let gradesChartInstance;
let extracurricularAttendanceChart;
const cookies = document.cookie.split('; ');
console.log(cookies)
let reports_keys = []
let reports_values = []
let extracurricular_reports_keys
let extracurricular_reports_values
let alumni_keys
let alumni_values
for (let cookie of cookies) {
    const [key, values] = cookie.split('=');
    if (values !== "\"\"" && key =="reports_keys"){
        reports_keys = values.split(":")
    }
    else if (values !== "\"\"" && key =="reports_values"){
        reports_values = values.split(":")
    }
    else if (values !== "\"\"" && key =="extracurricular_reports_keys"){
        extracurricular_reports_keys = values.replaceAll("\"", "").split(":")
    }
    else if (values !== "\"\"" && key =="extracurricular_reports_values"){
        extracurricular_reports_values = values.split(":")
    }
    else if (values !== "\"\"" && key =="alumni_keys"){
        alumni_keys = values.replaceAll("\"", "").split(":")
    }
    else if (values !== "\"\"" && key =="alumni_values"){
        alumni_values = values.split(":")
    }
}

function initializeCharts(isDarkMode) {
    const textColor = isDarkMode ? '#e5e7eb' : '#1f2937'; // gray-100 or gray-900
    const gridColor = isDarkMode ? '#4b5563' : '#e5e7eb'; // gray-600 or gray-200

    // Destroy existing chart instances if they exist
    if (attendanceChartInstance) {
        attendanceChartInstance.destroy();
    }
    if (gradesChartInstance) {
        gradesChartInstance.destroy();
    }
    if (extracurricularAttendanceChart) {
        extracurricularAttendanceChart.destroy();
    }

    const ctxAttendance = document.getElementById('attendanceChart').getContext('2d');
    
    attendanceChartInstance = new Chart(ctxAttendance, {
        type: 'bar',
        data: {
            labels: reports_keys,
            datasets: [{
                label: 'Pertemuan Ekskul (%)',
                data: reports_values,
                backgroundColor: isDarkMode ? 'rgba(75, 192, 192, 0.8)' : 'rgba(75, 192, 192, 0.6)',
                borderColor: isDarkMode ? 'rgba(75, 192, 192, 1)' : 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                borderRadius: 5,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 15,
                    ticks: {
                        color: textColor
                    },
                    grid: {
                        color: gridColor
                    }
                },
                x: {
                    ticks: {
                        color: textColor
                    },
                    grid: {
                        color: gridColor
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: textColor
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw + '%';
                        }
                    }
                }
            }
        }
    });

    if(extracurricular_reports_keys){

        const extracurricularAttendanceCtx = document.getElementById('extracurricularAttendanceChart').getContext('2d');
        extracurricularAttendanceChart = new Chart(extracurricularAttendanceCtx, {
            type: 'bar',
            data: {
                labels: extracurricular_reports_keys,
                datasets: [{
                    label: 'Pertemuan Ekskul (%)',
                    data: extracurricular_reports_values,
                    backgroundColor: isDarkMode ? 'rgba(75, 192, 192, 0.8)' : 'rgba(75, 192, 192, 0.6)',
                    borderColor: isDarkMode ? 'rgba(75, 192, 192, 1)' : 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    borderRadius: 5,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 15,
                        ticks: {
                            color: textColor
                        },
                        grid: {
                            color: gridColor
                        }
                    },
                    x: {
                        ticks: {
                            color: textColor
                        },
                        grid: {
                            color: gridColor
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: textColor
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.raw + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    else{
        document.getElementById('secondChart').style.display = 'none'
    }
    
    const ctxGrades = document.getElementById('gradesChart').getContext('2d');
    gradesChartInstance = new Chart(ctxGrades, {
        type: 'line',
        data: {
            labels: alumni_keys,
            datasets: [{
                label: 'Average Grade',
                data: alumni_values,
                backgroundColor: isDarkMode ? 'rgba(153, 102, 255, 0.4)' : 'rgba(153, 102, 255, 0.2)',
                borderColor: isDarkMode ? 'rgba(153, 102, 255, 1)' : 'rgba(153, 102, 255, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: textColor
                    },
                    grid: {
                        color: gridColor
                    }
                },
                x: {
                    ticks: {
                        color: textColor
                    },
                    grid: {
                        color: gridColor
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: textColor
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw;
                        }
                    }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', (event) => {
    lucide.createIcons();

    const htmlElement = document.documentElement;
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn'); // Mobile hamburger
    const closeSidebarBtn = document.getElementById('close-sidebar-btn'); // Mobile close
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mainContent = document.getElementById('main-content');
    const desktopSidebarToggleBtn = document.getElementById('desktop-sidebar-toggle-btn'); // Desktop toggle
    const desktopSidebarToggleIconLeft = document.getElementById('desktop-sidebar-toggle-icon-left'); // Icon for desktop toggle
    const desktopSidebarToggleIconRight = document.getElementById('desktop-sidebar-toggle-icon-right'); // Icon for desktop toggle
    const notificationsBellBtn = document.getElementById('notifications-bell-btn');
    const notificationsDropdown = document.getElementById('notifications-dropdown');
    const userAvatarContainer = document.getElementById('user-avatar-container');
    const userDropdown = document.getElementById('user-dropdown');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const darkModeIcon = document.getElementById('dark-mode-icon');

    // LLM Feature Elements
    const announcementPrompt = document.getElementById('announcement-prompt');
    const generateAnnouncementBtn = document.getElementById('generate-announcement-btn');
    const generateSpinner = document.getElementById('generate-spinner');
    const announcementOutputContainer = document.getElementById('announcement-output-container');
    const announcementOutput = document.getElementById('announcement-output');
    const copyAnnouncementBtn = document.getElementById('copy-announcement-btn');
    


    desktopSidebarToggleBtn.addEventListener("click", ()=>{
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true'){
            document.getElementById('desktop-sidebar-toggle-icon-right').classList.add("hidden");
            document.getElementById('desktop-sidebar-toggle-icon-left').classList.remove("hidden");
        } else {
            document.getElementById('desktop-sidebar-toggle-icon-right').classList.remove("hidden");
            document.getElementById('desktop-sidebar-toggle-icon-left').classList.add("hidden");
            
        }
    })

    // Function to save sidebar state to local storage
    function saveSidebarState(isCollapsed) {
        localStorage.setItem('sidebarCollapsed', isCollapsed ? true : false);
    }

    // Function to load sidebar state from local storage
    function loadSidebarState() {
        const savedState = localStorage.getItem('sidebarCollapsed');
        return savedState === 'true'; // Returns true if 'true', false otherwise (including null)
    }

    // Function to apply sidebar state (collapsed/expanded)
    function applySidebarState(collapsedState) {
        if (collapsedState) {
            sidebar.classList.add('collapsed'); // Use 'collapsed' class for desktop
            document.getElementById('desktop-sidebar-toggle-icon-left').classList.add("hidden");
            document.getElementById('desktop-sidebar-toggle-icon-right').classList.remove("hidden");
        } else {
            sidebar.classList.remove('collapsed'); // Remove 'collapsed' class
            document.getElementById('desktop-sidebar-toggle-icon-left').classList.remove("hidden");
            document.getElementById('desktop-sidebar-toggle-icon-right').classList.add("hidden");
        }
        lucide.createIcons(); // Re-render icon after state change
    }

    // Function to toggle sidebar visibility (mobile vs. desktop behavior)
    function toggleSidebar(e) {
        if (window.innerWidth < 768) {
            // Mobile behavior: slide in/out
            sidebar.classList.toggle('active'); // Toggles 'active' for mobile slide-in/out
            sidebarOverlay.classList.toggle('active');
        } 
        else {
            // Desktop behavior: collapse/expand
            const isCurrentlyCollapsed = localStorage.getItem('sidebarCollapsed');
            applySidebarState(!(isCurrentlyCollapsed=="true")); // Toggle and apply
            saveSidebarState(!(isCurrentlyCollapsed=="true")); // Save the new state
        }
    }

    // Event listeners for mobile and desktop toggles
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', toggleSidebar);
    }
    if (closeSidebarBtn) {
        closeSidebarBtn.addEventListener('click', toggleSidebar);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleSidebar); // Close mobile sidebar when clicking overlay
    }

    sidebar.addEventListener("mouseout", (e)=>{
        console.log("Hai")
    })
    
    

    if (desktopSidebarToggleBtn) {
        desktopSidebarToggleBtn.addEventListener('click', toggleSidebar);
    }

    // Initial state on load and resize
    function handleResize() {
        if (window.innerWidth >= 768) {
            // On desktop:
            // Ensure mobile-specific classes are removed
            sidebar.classList.remove('active', 'sidebar-mobile');
            sidebarOverlay.classList.remove('active');

            // Add desktop-specific classes
            sidebar.classList.add('sidebar-desktop');
            mainContent.classList.add('main-content-desktop');

            // Load state from local storage or default to expanded
            const savedCollapsedState = loadSidebarState();
            applySidebarState(savedCollapsedState); // Apply the loaded or default state

        } else {
            // On mobile:
            // Ensure desktop-specific classes are removed
            sidebar.classList.remove('collapsed', 'sidebar-desktop');

            // Ensure mobile-specific classes are applied for initial hidden state
            sidebar.classList.add('sidebar-mobile');
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
            mainContent.classList.add('main-content-mobile'); // Ensure no margin on mobile
        }
        lucide.createIcons(); // Re-render icons after potential data-lucide changes
    }

    window.addEventListener('resize', handleResize);
    handleResize(); // Call on initial load to set correct state

    // Notifications Dropdown Logic
    if (notificationsBellBtn && notificationsDropdown) {
        notificationsBellBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent document click from immediately closing it
            notificationsDropdown.classList.toggle('active');
            notificationsDropdown.classList.toggle('hidden');
            userDropdown.classList.remove('active'); // Close user dropdown if open
            userDropdown.classList.add('hidden');

        });

        document.addEventListener('click', (e) => {
            // Close dropdown if click is outside the dropdown and the bell button
            if (!notificationsDropdown.contains(e.target) && !notificationsBellBtn.contains(e.target)) {
                notificationsDropdown.classList.remove('active');
                notificationsDropdown.classList.add('hidden');

            }
        });
    }

    // User Avatar Dropdown Logic
    if (userAvatarContainer && userDropdown) {
        userAvatarContainer.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent document click from immediately closing it
            userDropdown.classList.toggle('active');
            userDropdown.classList.toggle('hidden');
            notificationsDropdown.classList.remove('active'); // Close notifications dropdown if open
            notificationsDropdown.classList.add('hidden');

        });

        document.addEventListener('click', (e) => {
            // Close dropdown if click is outside the dropdown and the avatar container
            if (!userDropdown.contains(e.target) && !userAvatarContainer.contains(e.target)) {
                userDropdown.classList.remove('active');
                userDropdown.classList.add('hidden');
            }
        });
    }

    // Dark Mode Logic
    function applyDarkMode(isDark) {
        if (isDark) {
            htmlElement.classList.add('dark');
            darkModeIcon.setAttribute('data-lucide', 'sun');
        } else {
            htmlElement.classList.remove('dark');
            darkModeIcon.setAttribute('data-lucide', 'moon');
        }
        lucide.createIcons(); // Re-render icon
        initializeCharts(isDark); // Re-initialize charts with new theme
    }

    // Load dark mode preference from local storage
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        applyDarkMode(true);
    } else {
        applyDarkMode(false); // Default to light mode if no preference or 'false'
    }

    // Toggle dark mode on button click
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            const isDark = htmlElement.classList.contains('dark');
            applyDarkMode(!isDark);
            localStorage.setItem('darkMode', !isDark);
        });
    }

    // LLM Feature: Generate Announcement Draft
    if (generateAnnouncementBtn) {
        generateAnnouncementBtn.addEventListener('click', async () => {
            const promptText = announcementPrompt.value.trim();
            if (!promptText) {
                alert('Please enter a description for the announcement.');
                return;
            }

            generateSpinner.classList.remove('hidden');
            generateAnnouncementBtn.disabled = true;
            announcementOutputContainer.classList.add('hidden');
            announcementOutput.value = '';

            try {
                let chatHistory = [];
                chatHistory.push({ role: "user", parts: [{ text: `Draft a school announcement based on the following details: "${promptText}". Make it professional, engaging, and suitable for a school audience. Include a clear call to action if appropriate.` }] });
                const payload = { contents: chatHistory };
                const apiKey = ""; // Leave as empty string for Canvas to provide
                const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });

                const result = await response.json();

                if (result.candidates && result.candidates.length > 0 &&
                    result.candidates[0].content && result.candidates[0].content.parts &&
                    result.candidates[0].content.parts.length > 0) {
                    const text = result.candidates[0].content.parts[0].text;
                    announcementOutput.value = text;
                    announcementOutputContainer.classList.remove('hidden');
                } else {
                    announcementOutput.value = 'Error: Could not generate announcement. Please try again.';
                    announcementOutputContainer.classList.remove('hidden');
                    console.error('Gemini API response structure unexpected:', result);
                }
            } catch (error) {
                announcementOutput.value = 'Error generating announcement: ' + error.message;
                announcementOutputContainer.classList.remove('hidden');
                console.error('Error calling Gemini API:', error);
            } finally {
                generateSpinner.classList.add('hidden');
                generateAnnouncementBtn.disabled = false;
            }
        });
    }

    // Copy to Clipboard Logic
    if (copyAnnouncementBtn) {
        copyAnnouncementBtn.addEventListener('click', () => {
            announcementOutput.select();
            document.execCommand('copy');
            // Provide visual feedback
            const originalText = copyAnnouncementBtn.textContent;
            copyAnnouncementBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyAnnouncementBtn.textContent = originalText;
            }, 2000);
        });
    }

    // Initial chart render based on current mode
    initializeCharts(htmlElement.classList.contains('dark'));
});