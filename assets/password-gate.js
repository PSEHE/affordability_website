(function() {
    const PASSWORD = 'PSE';
    const SESSION_KEY = 'site-pass-ok';

    try {
        if (sessionStorage.getItem(SESSION_KEY) === 'yes') {
            return;
        }

        const entered = prompt('Enter password to view this site:');
        if (entered !== PASSWORD) {
            document.body.innerHTML = '<h1 style="text-align:center;margin-top:3rem;">Access denied</h1>';
            throw new Error('Incorrect password');
        }

        sessionStorage.setItem(SESSION_KEY, 'yes');
    } catch (error) {
        console.error('Password gate blocked access:', error);
        throw error;
    }
})();
