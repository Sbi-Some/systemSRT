// SRT System Main JavaScript

// Configuration globale
const SRT = {
    config: {
        apiBaseUrl: '/api',
        refreshInterval: 30000, // 30 secondes
        mapCenter: [46.603354, 1.888334],
        mapZoom: 6
    },
    
    // État global de l'application
    state: {
        user: null,
        notifications: [],
        activeAlerts: [],
        sidebarOpen: true
    },
    
    // Utilitaires
    utils: {
        // Formatage des dates
        formatDate: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('fr-FR', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        // Formatage des nombres
        formatNumber: function(num) {
            return new Intl.NumberFormat('fr-FR').format(num);
        },
        
        // Génération d'ID unique
        generateId: function() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2);
        },
        
        // Debounce pour les recherches
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Validation des coordonnées GPS
        isValidCoordinate: function(lat, lng) {
            return lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
        }
    },
    
    // Système de notifications
    notifications: {
        show: function(type, title, message, duration = 5000) {
            const notification = {
                id: SRT.utils.generateId(),
                type: type,
                title: title,
                message: message,
                timestamp: new Date()
            };
            
            SRT.state.notifications.push(notification);
            this.render(notification);
            
            if (duration > 0) {
                setTimeout(() => {
                    this.remove(notification.id);
                }, duration);
            }
            
            return notification.id;
        },
        
        render: function(notification) {
            const container = document.getElementById('notification-container') || this.createContainer();
            
            const element = document.createElement('div');
            element.id = `notification-${notification.id}`;
            element.className = `notification-toast ${notification.type} mb-4 p-4 rounded-lg shadow-lg`;
            
            element.innerHTML = `
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        ${this.getIcon(notification.type)}
                    </div>
                    <div class="ml-3 flex-1">
                        <h4 class="text-sm font-medium text-white">${notification.title}</h4>
                        <p class="text-sm text-gray-300 mt-1">${notification.message}</p>
                    </div>
                    <div class="ml-4 flex-shrink-0">
                        <button onclick="SRT.notifications.remove('${notification.id}')" 
                                class="text-gray-400 hover:text-white">
                            <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
            
            container.appendChild(element);
        },
        
        remove: function(id) {
            const element = document.getElementById(`notification-${id}`);
            if (element) {
                element.style.transform = 'translateX(100%)';
                element.style.opacity = '0';
                setTimeout(() => {
                    element.remove();
                }, 300);
            }
            
            SRT.state.notifications = SRT.state.notifications.filter(n => n.id !== id);
        },
        
        createContainer: function() {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'fixed top-4 right-4 z-50 max-w-sm';
            document.body.appendChild(container);
            return container;
        },
        
        getIcon: function(type) {
            const icons = {
                success: '<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>',
                error: '<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>',
                warning: '<svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>',
                info: '<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>'
            };
            return icons[type] || icons.info;
        }
    },
    
    // Gestion des API
    api: {
        request: async function(endpoint, options = {}) {
            const url = `${SRT.config.apiBaseUrl}${endpoint}`;
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            };
            
            const config = { ...defaultOptions, ...options };
            
            try {
                const response = await fetch(url, config);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error('API Request Error:', error);
                SRT.notifications.show('error', 'Erreur API', error.message);
                throw error;
            }
        },
        
        get: function(endpoint) {
            return this.request(endpoint, { method: 'GET' });
        },
        
        post: function(endpoint, data) {
            return this.request(endpoint, {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        put: function(endpoint, data) {
            return this.request(endpoint, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },
        
        delete: function(endpoint) {
            return this.request(endpoint, { method: 'DELETE' });
        },
        
        getCSRFToken: function() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            return token ? token.value : '';
        }
    },
    
    // Gestion des cartes
    maps: {
        instances: {},
        
        create: function(containerId, options = {}) {
            const defaultOptions = {
                center: SRT.config.mapCenter,
                zoom: SRT.config.mapZoom,
                zoomControl: true,
                attributionControl: true
            };
            
            const config = { ...defaultOptions, ...options };
            const map = L.map(containerId).setView(config.center, config.zoom);
            
            // Ajouter la couche de tuiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
            
            this.instances[containerId] = map;
            return map;
        },
        
        addMarker: function(mapId, lat, lng, options = {}) {
            const map = this.instances[mapId];
            if (!map) return null;
            
            const marker = L.marker([lat, lng], options).addTo(map);
            return marker;
        },
        
        addThreatMarker: function(mapId, lat, lng, threat) {
            const colors = {
                'CRITICAL': 'red',
                'HIGH': 'orange',
                'MEDIUM': 'yellow',
                'LOW': 'green'
            };
            
            const color = colors[threat.threat_level] || 'blue';
            
            const marker = L.circleMarker([lat, lng], {
                color: color,
                fillColor: color,
                fillOpacity: 0.6,
                radius: 8
            });
            
            marker.bindPopup(`
                <div class="p-2">
                    <h3 class="font-bold text-sm">${threat.title}</h3>
                    <p class="text-xs mt-1">Niveau: ${threat.threat_level}</p>
                    <p class="text-xs">Date: ${SRT.utils.formatDate(threat.report_date)}</p>
                </div>
            `);
            
            const map = this.instances[mapId];
            if (map) {
                marker.addTo(map);
            }
            
            return marker;
        },
        
        loadReports: async function(mapId, filters = {}) {
            try {
                const params = new URLSearchParams(filters);
                const data = await SRT.api.get(`/intelligence/map-data/?${params}`);
                
                const map = this.instances[mapId];
                if (!map) return;
                
                // Effacer les marqueurs existants
                map.eachLayer(layer => {
                    if (layer instanceof L.CircleMarker) {
                        map.removeLayer(layer);
                    }
                });
                
                // Ajouter les nouveaux marqueurs
                data.reports.forEach(report => {
                    if (SRT.utils.isValidCoordinate(report.latitude, report.longitude)) {
                        this.addThreatMarker(mapId, report.latitude, report.longitude, report);
                    }
                });
                
            } catch (error) {
                console.error('Erreur lors du chargement des rapports:', error);
            }
        }
    },
    
    // Gestion des graphiques
    charts: {
        instances: {},
        
        create: function(canvasId, type, data, options = {}) {
            const ctx = document.getElementById(canvasId);
            if (!ctx) return null;
            
            const defaultOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                },
                scales: type !== 'doughnut' && type !== 'pie' ? {
                    x: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                } : {}
            };
            
            const config = {
                type: type,
                data: data,
                options: { ...defaultOptions, ...options }
            };
            
            const chart = new Chart(ctx, config);
            this.instances[canvasId] = chart;
            return chart;
        },
        
        update: function(chartId, newData) {
            const chart = this.instances[chartId];
            if (chart) {
                chart.data = newData;
                chart.update();
            }
        },
        
        destroy: function(chartId) {
            const chart = this.instances[chartId];
            if (chart) {
                chart.destroy();
                delete this.instances[chartId];
            }
        }
    },
    
    // Gestion des formulaires
    forms: {
        validate: function(formElement) {
            const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    this.showFieldError(input, 'Ce champ est requis');
                    isValid = false;
                } else {
                    this.clearFieldError(input);
                }
            });
            
            return isValid;
        },
        
        showFieldError: function(field, message) {
            this.clearFieldError(field);
            
            field.classList.add('border-red-500');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'text-red-500 text-sm mt-1 field-error';
            errorDiv.textContent = message;
            
            field.parentNode.appendChild(errorDiv);
        },
        
        clearFieldError: function(field) {
            field.classList.remove('border-red-500');
            
            const errorDiv = field.parentNode.querySelector('.field-error');
            if (errorDiv) {
                errorDiv.remove();
            }
        },
        
        serialize: function(formElement) {
            const formData = new FormData(formElement);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                if (data[key]) {
                    if (Array.isArray(data[key])) {
                        data[key].push(value);
                    } else {
                        data[key] = [data[key], value];
                    }
                } else {
                    data[key] = value;
                }
            }
            
            return data;
        }
    },
    
    // Gestion des modales
    modals: {
        open: function(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('hidden');
                modal.classList.add('flex');
                document.body.style.overflow = 'hidden';
            }
        },
        
        close: function(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
                document.body.style.overflow = 'auto';
            }
        },
        
        closeAll: function() {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            });
            document.body.style.overflow = 'auto';
        }
    },
    
    // Initialisation
    init: function() {
        console.log('SRT System initializing...');
        
        // Initialiser les notifications
        this.notifications.createContainer();
        
        // Initialiser les mises à jour en temps réel
        this.startRealTimeUpdates();
        
        // Initialiser les gestionnaires d'événements globaux
        this.initEventHandlers();
        
        console.log('SRT System initialized successfully');
    },
    
    startRealTimeUpdates: function() {
        setInterval(async () => {
            try {
                const stats = await this.api.get('/dashboard/stats/');
                this.updateDashboardStats(stats);
            } catch (error) {
                console.error('Erreur lors de la mise à jour:', error);
            }
        }, this.config.refreshInterval);
    },
    
    updateDashboardStats: function(stats) {
        Object.keys(stats).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                element.textContent = this.utils.formatNumber(stats[key]);
            }
        });
    },
    
    initEventHandlers: function() {
        // Gestionnaire pour fermer les modales avec Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.modals.closeAll();
            }
        });
        
        // Gestionnaire pour les clics sur les overlays de modales
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.modals.closeAll();
            }
        });
        
        // Gestionnaire pour la sidebar mobile
        const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                SRT.state.sidebarOpen = !SRT.state.sidebarOpen;
                const sidebar = document.querySelector('.srt-sidebar');
                if (sidebar) {
                    sidebar.classList.toggle('open', SRT.state.sidebarOpen);
                }
            });
        }
    }
};

// Fonctions utilitaires globales
window.showNotification = function(type, title, message, duration) {
    return SRT.notifications.show(type, title, message, duration);
};

window.openModal = function(modalId) {
    SRT.modals.open(modalId);
};

window.closeModal = function(modalId) {
    SRT.modals.close(modalId);
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    SRT.init();
});

// Export pour utilisation dans d'autres scripts
window.SRT = SRT;