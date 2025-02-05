document.addEventListener('DOMContentLoaded', function() {
    const leagueSelect = document.getElementById('league_id');
    const groupSelect = document.getElementById('group_id');
    const yearSelect = document.getElementById('season_id');
    const customUrlInput = document.getElementById('custom_url');

    // When league is selected, populate groups and years
    leagueSelect.addEventListener('change', function() {
        const selectedLeague = this.value;

        if (selectedLeague) {
            customUrlInput.disabled = true;
            const leagueData = predefinedUrls[selectedLeague];

            // Populate groups and select first one
            groupSelect.innerHTML = '<option value="">Selecciona un grupo...</option>';
            const groupEntries = Object.entries(leagueData.groups);
            groupEntries.forEach(([groupName, groupId]) => {
                const option = new Option(groupName, groupId);
                groupSelect.add(option);
            });
            groupSelect.disabled = false;
            // Select first group automatically
            if (groupSelect.options.length > 1) {
                groupSelect.selectedIndex = 1;
            }

            // Populate years and select first one
            yearSelect.innerHTML = '<option value="">Selecciona un año...</option>';
            const seasonEntries = Object.entries(leagueData.seasons);
            seasonEntries.forEach(([seasonName, seasonId]) => {
                const option = new Option(seasonName, seasonId);
                yearSelect.add(option);
            });
            yearSelect.disabled = false;
            // Select last season automatically
            if (yearSelect.options.length > 1) {
                yearSelect.selectedIndex = yearSelect.options.length - 1;
            }

        } else {
            // Reset and disable dependent selectors
            groupSelect.innerHTML = '<option value="">Selecciona un grupo...</option>';
            yearSelect.innerHTML = '<option value="">Selecciona un año...</option>';
            groupSelect.disabled = true;
            yearSelect.disabled = true;
            customUrlInput.disabled = false;
        }
    });

    // When using custom URL, disable the selectors
    customUrlInput.addEventListener('input', function() {
        if (this.value) {
            leagueSelect.disabled = true;
            groupSelect.disabled = true;
            yearSelect.disabled = true;
        } else {
            leagueSelect.disabled = false;
            // Only enable others if league is selected
            const hasLeague = leagueSelect.value !== "";
            groupSelect.disabled = !hasLeague;
            yearSelect.disabled = !hasLeague;
        }
    });
});