const API_BASE_URL = 'http://127.0.0.1:5000/users';

        const apiClient = axios.create({
            baseURL: API_BASE_URL,
            headers: { 'Content-Type': 'application/json' },
        });

        apiClient.interceptors.request.use(
            config => {
                const token = localStorage.getItem('authToken');
                if (token) config.headers.Authorization = `Bearer ${token}`;
                return config;
            },
            error => Promise.reject(error)
        );

        Vue.createApp({
            data() {
                return {
                    loggedIn: false,
                    loading: false,
                    loginError: '',
                    loginForm: { username: '', password: '' },

                    showRegister: false,
                    registerError: '',
                    registerSuccess: false,
                    registerForm: { name: '', email: '', password: '', confirmPassword: '', phone_num: '' },

                    currentUser: { id: null, username: '', role: '' },
                    selectedPage: 'dashboard',

                    // Data States
                    treksLoading: false,
                    treks: [],
                    assignedTreks: [],

                    bookingsLoading: false,
                    allBookings: [],

                    staffListLoading: false,
                    staffList: [],
                    usersLoading: false,
                    usersList: [],

                    // Trek Creation Form
                    showCreateTrekForm: false,
                    newTrek: { 
                        trek_name: '', 
                        price: '', 
                        location: '', 
                        difficulty: 'Easy', 
                        duration: '', 
                        available_slots: '', 
                        assigned_slot: '',
                        assigned_staff_id: '', 
                        status: 'open', 
                        start_date: '', 
                        end_date: '' 
                    },

                    // Staff creation for admin
                    showCreateStaffForm: false,
                    newStaff: {
                        username: '',
                        email: '',
                        password: '',
                        confirmPassword: '',
                        phone_num: ''
                    },
                    staffCreateError: '',
                    staffCreateSuccess: false,
                    searchTrekQuery: '',
                    searchTrekStatus: '',
                    searchTrekDifficulty: '',
                    searchStaffQuery: '',
                    searchUserQuery: ''
                };
            },
            computed: {
                navLinks() {
                    const role = this.currentUser.role;
                    const links = [{ text: 'Dashboard', key: 'dashboard' }];

                    if (role === 'admin') {
                        links.push({ text: 'Treks', key: 'treks' });
                        links.push({ text: 'Bookings', key: 'bookings' });
                        links.push({ text: 'Staff', key: 'staff' });
                        links.push({ text: 'Users', key: 'users' });
                    } else if (role === 'staff') {
                        links.push({ text: 'Assigned Treks', key: 'assigned-treks' });
                        links.push({ text: 'All Treks', key: 'treks' });
                        links.push({ text: 'Bookings', key: 'bookings' });
                    } else {
                        links.push({ text: 'Browse Treks', key: 'treks' });
                        links.push({ text: 'My Bookings', key: 'bookings' });
                    }
                    return links;
                }
            },
            mounted() {
                const savedUser = localStorage.getItem('userData');
                if (savedUser) {
                    try {
                        this.currentUser = JSON.parse(savedUser);
                        this.loggedIn = true;
                        this.loadInitialData();
                    } catch (e) {
                        localStorage.removeItem('userData');
                    }
                }
            },
            methods: {
                clearMessages() {
                    this.loginError = '';
                    this.registerError = '';
                    this.registerSuccess = false;
                },
                selectPage(key) {
                    this.selectedPage = key;
                    if (key === 'treks') this.fetchTreks();
                    if (key === 'bookings') this.fetchAllBookings();
                    if (key === 'staff') this.fetchStaff();
                    if (key === 'users') this.fetchUsers();
                    if (key === 'assigned-treks') this.fetchAssignedTreks();
                },
                loadInitialData() {
                    this.fetchTreks();
                    if (this.currentUser.role === 'staff') {
                        this.fetchAssignedTreks();
                    }
                    if (this.currentUser.role === 'admin') {
                        this.fetchStaff();
                        this.fetchUsers();
                        this.fetchAllBookings();
                    } else if (this.currentUser.role === 'user') {
                        this.fetchAllBookings();
                    }
                },
                validateDateFormat(dateStr) {
                    const regex = /^\d{4}-\d{2}-\d{2}$/;
                    if (!regex.test(dateStr)) return false;
                    const d = new Date(dateStr);
                    return d instanceof Date && !isNaN(d) && d.toISOString().slice(0, 10) === dateStr;
                },
                getStatusBadgeClass(status) {
                    switch (status) {
                        case 'open': return 'bg-success';
                        case 'started': return 'bg-warning text-dark';
                        case 'approved': return 'bg-primary';
                        case 'pending': return 'bg-warning text-dark';
                        case 'complete': return 'bg-info text-dark';
                        case 'closed': return 'bg-secondary';
                        default: return 'bg-secondary';
                    }
                },
                parseJwt(token) {
                    if (!token) return null;
                    const parts = token.split('.');
                    if (parts.length !== 3) return null;
                    const base64Url = parts[1];
                    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                    try {
                        const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => '%'+('00'+c.charCodeAt(0).toString(16)).slice(-2)).join(''));
                        return JSON.parse(jsonPayload);
                    } catch (error) {
                        console.error('Failed to decode JWT payload:', error);
                        return null;
                    }
                },

                // --- AUTHENTICATION ---
                async handleLogin() {
                    this.loading = true;
                    this.loginError = '';
                    try {
                        const res = await apiClient.post('/login', {
                            username: this.loginForm.username,
                            password: this.loginForm.password
                        });

                        const token = res.data.token;
                        if (token) {
                            localStorage.setItem('authToken', token);
                        }

                        const payload = this.parseJwt(token);
                        const loggedUserId = res.data.user_id || res.data.id || payload?.sub || payload?.identity;
                        const username = payload?.username || res.data.username || this.loginForm.username;
                        const role = payload?.role || res.data.role || res.data.type_of_user || 'user';

                        if (!loggedUserId) {
                            console.error('Login response missing user ID:', res.data, payload);
                            alert('Login succeeded, but backend did not return a user_id!');
                            return;
                        }

                        const user = {
                            id: parseInt(loggedUserId),
                            username,
                            role
                        };

                        this.currentUser = user;
                        this.loggedIn = true;
                        localStorage.setItem('userData', JSON.stringify(user));

                        this.selectedPage = 'dashboard';
                        this.loadInitialData();
                    } catch (error) {
                        this.loginError = error.response?.data?.message || 'Invalid username or password.';
                    } finally {
                        this.loading = false;
                    }
                },
                async handleRegister() {
                    this.loading = true;
                    this.registerError = '';
                    this.registerSuccess = false;

                    if (this.registerForm.password !== this.registerForm.confirmPassword) {
                        this.registerError = 'Passwords do not match.';
                        this.loading = false;
                        return;
                    }

                    try {
                        await apiClient.post('/register', {
                            username: this.registerForm.name.trim(),
                            email_id: this.registerForm.email.trim(),
                            password: this.registerForm.password,
                            phone_num: this.registerForm.phone_num
                        });
                        this.registerSuccess = true;
                        this.registerForm = { name: '', email: '', password: '', confirmPassword: '', phone_num: '' };
                    } catch (error) {
                        this.registerError = error.response?.data?.message || 'Registration failed.';
                    } finally {
                        this.loading = false;
                    }
                },
                handleLogout() {
                    localStorage.removeItem('authToken');
                    localStorage.removeItem('userData');
                    this.loggedIn = false;
                    this.currentUser = { id: null, username: '', role: '' };
                },

                // --- DATA FETCHING ---
                async fetchTreks() {
                    this.treksLoading = true;
                    try {
                        const res = await apiClient.get('/get_trek');
                        this.treks = Array.isArray(res.data) ? res.data : [];
                    } catch (error) {
                        console.error('Failed to fetch treks:', error);
                    } finally {
                        this.treksLoading = false;
                    }
                },
                async fetchAssignedTreks() {
                    if (!this.currentUser.id) return;
                    this.treksLoading = true;
                    try {
                        const res = await apiClient.get(`/get_assigned_treks/${this.currentUser.id}`);
                        this.assignedTreks = Array.isArray(res.data) ? res.data : [];
                    } catch (error) {
                        console.error('Failed to fetch assigned treks:', error);
                    } finally {
                        this.treksLoading = false;
                    }
                },
                async searchTreks() {
                    const query = this.searchTrekQuery?.trim();
                    const status = this.searchTrekStatus;
                    const difficulty = this.searchTrekDifficulty;

                    if (!query && !status && !difficulty) {
                        return this.fetchTreks();
                    }

                    try {
                        const res = await apiClient.get(`/search_treks/${this.currentUser.id}`, {
                            params: {
                                q: query || undefined,
                                status: status || undefined,
                                difficulty: difficulty || undefined,
                            }
                        });
                        this.treks = Array.isArray(res.data) ? res.data : [];
                    } catch (error) {
                        console.error('Failed to search treks:', error);
                        this.treks = [];
                    }
                },
                clearTrekSearch() {
                    this.searchTrekQuery = '';
                    this.searchTrekStatus = '';
                    this.searchTrekDifficulty = '';
                    this.fetchTreks();
                },
                async searchStaff() {
                    if (!this.currentUser.role || this.currentUser.role !== 'admin') {
                        return;
                    }

                    const query = this.searchStaffQuery?.trim();
                    if (!query) {
                        return this.fetchStaff();
                    }

                    try {
                        const res = await apiClient.get(`/search_staff/${this.currentUser.id}`, { params: { q: query } });
                        this.staffList = Array.isArray(res.data) ? res.data : [];
                    } catch (error) {
                        console.error('Failed to search staff:', error);
                        this.staffList = [];
                    }
                },
                clearStaffSearch() {
                    this.searchStaffQuery = '';
                    this.fetchStaff();
                },
                async searchUsers() {
                    if (!this.currentUser.role || this.currentUser.role !== 'admin') {
                        return;
                    }

                    const query = this.searchUserQuery?.trim();
                    if (!query) {
                        return this.fetchUsers();
                    }

                    try {
                        const res = await apiClient.get(`/search_users/${this.currentUser.id}`, { params: { q: query } });
                        this.usersList = Array.isArray(res.data) ? res.data : [];
                    } catch (error) {
                        console.error('Failed to search users:', error);
                        this.usersList = [];
                    }
                },
                clearUserSearch() {
                    this.searchUserQuery = '';
                    this.fetchUsers();
                },
                async handleUpdateAssignedTrekStatus(trek, status) {
                    if (!this.currentUser.id || !trek?.trek_id) return;
                    this.loading = true;
                    try {
                        await apiClient.post(`/update_trek/${this.currentUser.id}/${trek.trek_id}`, { status });
                        await this.fetchAssignedTreks();
                        alert(`Trek marked as ${status}.`);
                    } catch (error) {
                        alert(error.response?.data?.message || 'Failed to update trek status.');
                    } finally {
                        this.loading = false;
                    }
                },
                async fetchStaff() {
                    this.staffListLoading = true;
                    if (!this.currentUser?.id) {
                        this.staffListLoading = false;
                        return;
                    }
                    try {
                        const res = await apiClient.get(`/get_all_staff/${this.currentUser.id}`);
                        this.staffList = Array.isArray(res.data) ? res.data : [];
                    } catch (error) {
                        console.error('Failed to fetch staff:', error);
                        this.staffList = [];
                    } finally {
                        this.staffListLoading = false;
                    }
                },
                async fetchUsers() {
                    this.usersLoading = true;
                    if (!this.currentUser?.id) {
                        this.usersLoading = false;
                        return;
                    }
                    try {
                        const res = await apiClient.get(`/get_all_users/${this.currentUser.id}`);
                        this.usersList = Array.isArray(res.data) ? res.data : [];
                    } catch (error) {
                        console.error('Failed to fetch users:', error);
                        this.usersList = [];
                    } finally {
                        this.usersLoading = false;
                    }
                },
                async handleToggleUserActivation(person) {
                    if (!this.currentUser?.id || !person?.user_id) return;
                    const action = person.is_active ? 'deactivate' : 'reactivate';
                    if (!confirm(`${action.charAt(0).toUpperCase() + action.slice(1)} ${person.user_name || person.username || 'this user'}?`)) return;

                    this.loading = true;
                    try {
                        const endpoint = person.is_active
                            ? `/deactivate_user/${this.currentUser.id}/${person.user_id}`
                            : `/activate_user/${this.currentUser.id}/${person.user_id}`;
                        await apiClient.post(endpoint);
                        if (this.selectedPage === 'users') {
                            await this.fetchUsers();
                        } else {
                            await this.fetchStaff();
                        }
                        alert(`User has been ${person.is_active ? 'deactivated' : 'reactivated'}.`);
                    } catch (error) {
                        alert(error.response?.data?.message || `Failed to ${action} user.`);
                    } finally {
                        this.loading = false;
                    }
                },
                async fetchAllBookings() {
                    this.bookingsLoading = true;
                    if (!this.currentUser?.id) {
                        this.bookingsLoading = false;
                        return;
                    }
                    try {
                        const url = this.currentUser.role === 'admin'
                            ? `/get_all_bookings/${this.currentUser.id}`
                            : `/get_bookings/${this.currentUser.id}`;
                        const res = await apiClient.get(url);
                        this.allBookings = Array.isArray(res.data) ? res.data : [];
                    } catch (error) {
                        console.error('Failed to fetch bookings:', error);
                        this.allBookings = [];
                    } finally {
                        this.bookingsLoading = false;
                    }
                },

                // --- ACTION HANDLERS ---
                async handleCreateTrek() {
                    if (!this.validateDateFormat(this.newTrek.start_date) || !this.validateDateFormat(this.newTrek.end_date)) {
                        alert('Invalid date format! Please enter start_date and end_date in YYYY-MM-DD format.');
                        return;
                    }

                    this.loading = true;
                    try {
                        const payload = {
                            trek_name: this.newTrek.trek_name,
                            location: this.newTrek.location,
                            price: parseFloat(this.newTrek.price),
                            duration: parseInt(this.newTrek.duration),
                            difficulty: this.newTrek.difficulty,
                            available_slots: String(this.newTrek.available_slots),
                            assigned_slot: this.newTrek.assigned_slot || null,
                            assigned_staff_id: parseInt(this.newTrek.assigned_staff_id),
                            status: this.newTrek.status,
                            start_date: this.newTrek.start_date,
                            end_date: this.newTrek.end_date
                        };

                        await apiClient.post(`/create_trek/${this.currentUser.id}`, payload);
                        alert('Trek created successfully!');
                        this.showCreateTrekForm = false;
                        
                        this.newTrek = { 
                            trek_name: '', 
                            price: '', 
                            location: '', 
                            difficulty: 'Easy', 
                            duration: '', 
                            available_slots: '', 
                            assigned_slot: '',
                            assigned_staff_id: '', 
                            status: 'open', 
                            start_date: '', 
                            end_date: '' 
                        };
                        
                        this.fetchTreks();
                    } catch (error) {
                        alert(error.response?.data?.message || 'Failed to create trek.');
                    } finally {
                        this.loading = false;
                    }
                },
                async handleCreateStaff() {
                    this.staffCreateError = '';
                    this.staffCreateSuccess = false;

                    if (this.newStaff.password !== this.newStaff.confirmPassword) {
                        this.staffCreateError = 'Passwords do not match.';
                        return;
                    }

                    this.loading = true;
                    try {
                        await apiClient.post(`/register_staff/${this.currentUser.id}`, {
                            username: this.newStaff.username.trim(),
                            password: this.newStaff.password,
                            email_id: this.newStaff.email.trim(),
                            phone_num: this.newStaff.phone_num.trim()
                        });
                        this.staffCreateSuccess = true;
                        this.showCreateStaffForm = false;
                        this.newStaff = { username: '', email: '', password: '', confirmPassword: '', phone_num: '' };
                        await this.fetchStaff();
                    } catch (error) {
                        this.staffCreateError = error.response?.data?.message || 'Failed to create staff.';
                    } finally {
                        this.loading = false;
                    }
                },
                async handleCreateBooking(trek) {
                    // Log trek object to inspect keys in Browser Developer Tools (F12 -> Console)
                    console.log('Selected Trek Data:', trek);

                    // Fallback through common primary key names
                    const trekId = trek.trek_id || trek.id || trek.id_trek || trek._id;

                    if (!trekId) {
                        alert('Could not determine Trek ID. Check API response keys.');
                        return;
                    }

                    this.loading = true;
                    try {
                        const payload = {
                            user_id: parseInt(this.currentUser.id),
                            trek_id: parseInt(trekId)
                        };
                        await apiClient.post('/create_booking', payload);
                        alert(`Booking request sent for ${trek.trek_name || trek.name || 'Trek'}!`);
                        this.fetchTreks();
                    } catch (error) {
                        alert(error.response?.data?.message || 'Booking failed.');
                    } finally {
                        this.loading = false;
                    }
                }
            }
        }).mount('#app');