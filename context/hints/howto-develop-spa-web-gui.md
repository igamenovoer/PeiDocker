# Single-Page Application Web GUI Design Guidelines for PeiDocker

## Overview

This guide provides comprehensive design principles and best practices for developing a single-page application (SPA) web GUI for PeiDocker - a Docker automation framework that transforms YAML configurations into reproducible containerized environments.

## What is a Single-Page Application (SPA)?

A single-page application is a web application that loads a single HTML page and dynamically updates content without requiring full page reloads. SPAs provide:

- **Faster user interactions** - Only data is transferred, not entire HTML pages
- **Desktop-like experience** - Smooth transitions and responsive interactions
- **Improved performance** - Reduced server requests and bandwidth usage
- **Better user experience** - No page refresh interruptions

## Core SPA Architecture Principles

### 1. Component-Based Architecture
Structure your application using reusable, modular components:

```javascript
// Example: Configuration form component
const ConfigForm = {
  props: ['config'],
  template: `
    <form @submit.prevent="handleSubmit">
      <input v-model="localConfig.name" placeholder="Container name" />
      <textarea v-model="localConfig.description"></textarea>
      <button type="submit">Save Configuration</button>
    </form>
  `,
  methods: {
    handleSubmit() {
      this.$emit('config-updated', this.localConfig);
    }
  }
};
```

### 2. Client-Side Routing
Implement navigation without page reloads:

```javascript
// Vue Router example for PeiDocker sections
const routes = [
  { path: '/', component: Dashboard },
  { path: '/configs', component: ConfigurationManager },
  { path: '/builds', component: BuildHistory },
  { path: '/containers', component: ContainerMonitor }
];
```

### 3. State Management
Centralize application state for consistency:

```javascript
// Vuex store example for Docker configurations
const store = new Vuex.Store({
  state: {
    configurations: [],
    activeBuilds: [],
    containerStatus: {}
  },
  mutations: {
    ADD_CONFIGURATION(state, config) {
      state.configurations.push(config);
    }
  }
});
```

## Framework Selection for PeiDocker

### Recommended: Vue.js
**Best choice for PeiDocker** due to:
- Gentle learning curve
- Excellent documentation
- Perfect balance of simplicity and power
- Great for configuration management interfaces

```vue
<template>
  <div class="docker-config-editor">
    <config-form :config="selectedConfig" @save="saveConfiguration" />
    <build-status :builds="activeBuilds" />
  </div>
</template>
```

### Alternative: React
Good for complex interactions:
```jsx
function ConfigurationDashboard() {
  const [configs, setConfigs] = useState([]);
  
  return (
    <div className="dashboard">
      <ConfigList configs={configs} />
      <BuildMonitor />
    </div>
  );
}
```

### Alternative: Angular
Best for large-scale enterprise applications:
```typescript
@Component({
  selector: 'app-docker-manager',
  template: `
    <mat-sidenav-container>
      <mat-sidenav>Navigation</mat-sidenav>
      <mat-sidenav-content>
        <router-outlet></router-outlet>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `
})
export class DockerManagerComponent { }
```

## UI/UX Design Patterns for Configuration Management

### 1. Dashboard Layout
Apply F-pattern and Z-pattern reading:

```html
<!-- Primary information at top-left -->
<div class="dashboard-header">
  <h1>PeiDocker Control Panel</h1>
  <div class="quick-stats">
    <stat-card title="Active Builds" :value="activeBuilds.length" />
    <stat-card title="Configurations" :value="configs.length" />
  </div>
</div>

<!-- Main content in center -->
<div class="dashboard-content">
  <recent-builds />
  <configuration-overview />
</div>
```

### 2. Progressive Disclosure
Show information gradually to avoid overwhelming users:

```vue
<template>
  <div class="config-section">
    <!-- Basic settings always visible -->
    <basic-config v-model="config" />
    
    <!-- Advanced settings behind expandable section -->
    <collapsible-section title="Advanced Settings" v-model="showAdvanced">
      <advanced-config v-model="config.advanced" />
    </collapsible-section>
    
    <!-- Expert settings behind additional disclosure -->
    <collapsible-section title="Expert Options" v-model="showExpert" v-if="showAdvanced">
      <expert-config v-model="config.expert" />
    </collapsible-section>
  </div>
</template>
```

### 3. Form Design Best Practices

#### Validation and Error Handling
```vue
<template>
  <form @submit.prevent="validateAndSubmit" novalidate>
    <div class="form-group" :class="{ 'has-error': errors.containerName }">
      <label for="container-name">Container Name *</label>
      <input 
        id="container-name"
        v-model="form.containerName"
        :aria-describedby="errors.containerName ? 'container-name-error' : null"
        aria-required="true"
      />
      <div v-if="errors.containerName" id="container-name-error" class="error-message" role="alert">
        {{ errors.containerName }}
      </div>
    </div>
  </form>
</template>
```

#### Real-time Feedback
```javascript
// Provide immediate feedback for configuration validation
watch: {
  'config.ports': {
    handler(newPorts) {
      this.validatePorts(newPorts);
    },
    deep: true
  }
},
methods: {
  validatePorts(ports) {
    const validation = {
      isValid: true,
      warnings: [],
      errors: []
    };
    
    // Check for port conflicts
    ports.forEach(port => {
      if (this.isPortInUse(port)) {
        validation.warnings.push(`Port ${port} may be in use`);
      }
    });
    
    this.portValidation = validation;
  }
}
```

## Accessibility (WCAG 2.1) Implementation

### 1. Keyboard Navigation
```css
/* Ensure all interactive elements are keyboard accessible */
.config-button:focus,
.nav-link:focus {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}

/* Skip navigation for screen readers */
.skip-nav {
  position: absolute;
  top: -40px;
  left: 6px;
  background: #000;
  color: white;
  padding: 8px;
  text-decoration: none;
  transition: top 0.3s;
}

.skip-nav:focus {
  top: 6px;
}
```

### 2. Screen Reader Support
```vue
<template>
  <!-- Provide context for screen readers -->
  <section aria-labelledby="config-heading">
    <h2 id="config-heading">Docker Configuration</h2>
    
    <!-- Use ARIA labels for complex controls -->
    <div role="tabpanel" aria-labelledby="basic-tab" aria-describedby="basic-desc">
      <p id="basic-desc">Configure basic Docker container settings</p>
      <!-- Form content -->
    </div>
    
    <!-- Announce dynamic changes -->
    <div aria-live="polite" aria-atomic="true" class="sr-only">
      {{ statusMessage }}
    </div>
  </section>
</template>
```

### 3. Color and Contrast
```css
/* Ensure sufficient color contrast (4.5:1 ratio minimum) */
:root {
  --text-primary: #212529;      /* High contrast */
  --text-secondary: #6c757d;    /* Medium contrast */
  --border-color: #dee2e6;      /* Subtle borders */
  --success-color: #28a745;     /* Green with good contrast */
  --error-color: #dc3545;       /* Red with good contrast */
  --warning-color: #ffc107;     /* Yellow with dark text */
}

/* Don't rely solely on color for information */
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.status-indicator::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.status-running::before { color: var(--success-color); }
.status-error::before { color: var(--error-color); }
```

## Performance Optimization

### 1. Code Splitting
```javascript
// Lazy load heavy components
const ConfigurationEditor = () => import('./components/ConfigurationEditor.vue');
const BuildLogs = () => import('./components/BuildLogs.vue');

const routes = [
  {
    path: '/config/:id',
    component: ConfigurationEditor,
    // Only load when needed
  }
];
```

### 2. Data Management
```javascript
// Implement efficient data fetching
export default {
  data() {
    return {
      configurations: [],
      loading: false,
      pagination: {
        page: 1,
        size: 20,
        total: 0
      }
    };
  },
  methods: {
    async loadConfigurations() {
      this.loading = true;
      try {
        const response = await api.getConfigurations({
          page: this.pagination.page,
          size: this.pagination.size
        });
        this.configurations = response.data;
        this.pagination.total = response.total;
      } finally {
        this.loading = false;
      }
    }
  }
};
```

## Responsive Design Principles

### 1. Mobile-First Approach
```css
/* Start with mobile styles */
.config-panel {
  padding: 1rem;
  width: 100%;
}

/* Enhance for larger screens */
@media (min-width: 768px) {
  .config-panel {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }
}

@media (min-width: 1024px) {
  .config-panel {
    display: grid;
    grid-template-columns: 250px 1fr;
    gap: 2rem;
  }
}
```

### 2. Flexible Layouts
```vue
<template>
  <div class="responsive-layout">
    <!-- Collapsible sidebar on mobile -->
    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <navigation-menu />
    </aside>
    
    <!-- Main content area -->
    <main class="main-content">
      <header class="page-header">
        <button @click="toggleSidebar" class="sidebar-toggle" aria-label="Toggle navigation">
          ☰
        </button>
        <h1>{{ pageTitle }}</h1>
      </header>
      <router-view />
    </main>
  </div>
</template>
```

## Security Considerations

### 1. Input Validation
```javascript
// Client-side validation (never trust client-side only)
const configSchema = {
  containerName: {
    required: true,
    pattern: /^[a-zA-Z0-9][a-zA-Z0-9_.-]*$/,
    maxLength: 63
  },
  ports: {
    type: 'array',
    items: {
      type: 'number',
      minimum: 1,
      maximum: 65535
    }
  }
};

function validateConfiguration(config) {
  const errors = {};
  
  if (!config.containerName || !configSchema.containerName.pattern.test(config.containerName)) {
    errors.containerName = 'Invalid container name format';
  }
  
  return { isValid: Object.keys(errors).length === 0, errors };
}
```

### 2. API Communication
```javascript
// Secure API communication
const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
});

// Add CSRF token to requests
apiClient.interceptors.request.use(config => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }
  return config;
});
```

## Testing Strategy

### 1. Unit Testing
```javascript
// Vue Test Utils example
import { mount } from '@vue/test-utils';
import ConfigForm from '@/components/ConfigForm.vue';

describe('ConfigForm', () => {
  it('validates required fields', async () => {
    const wrapper = mount(ConfigForm);
    
    // Try to submit without required fields
    await wrapper.find('form').trigger('submit');
    
    expect(wrapper.find('.error-message').text()).toContain('Container name is required');
  });
  
  it('emits config-updated event on valid submission', async () => {
    const wrapper = mount(ConfigForm);
    
    await wrapper.find('#container-name').setValue('test-container');
    await wrapper.find('form').trigger('submit');
    
    expect(wrapper.emitted('config-updated')).toBeTruthy();
  });
});
```

### 2. Accessibility Testing
```javascript
// Using axe-core for automated accessibility testing
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('ConfigForm Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const wrapper = mount(ConfigForm);
    const results = await axe(wrapper.element);
    expect(results).toHaveNoViolations();
  });
});
```

## Progressive Enhancement Strategy

### 1. Core Functionality
Ensure basic functionality works without JavaScript:

```html
<!-- Form that works without JS -->
<form action="/api/configurations" method="POST">
  <input name="containerName" required />
  <button type="submit">Create Configuration</button>
</form>

<!-- Enhanced with JavaScript -->
<script>
document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('form');
  if (form) {
    // Add SPA functionality on top of working form
    enhanceWithVue(form);
  }
});
</script>
```

### 2. Graceful Degradation
```javascript
// Feature detection and fallbacks
if ('IntersectionObserver' in window) {
  // Use modern lazy loading
  implementLazyLoading();
} else {
  // Fallback to immediate loading
  loadAllImages();
}

// WebSocket with fallback to polling
if ('WebSocket' in window) {
  setupWebSocketConnection();
} else {
  setupPollingUpdates();
}
```

## Docker-Specific UI Patterns

### 1. Configuration Builder
```vue
<template>
  <div class="config-builder">
    <!-- Visual config builder -->
    <div class="config-steps">
      <step-indicator 
        v-for="(step, index) in configSteps" 
        :key="index"
        :step="step" 
        :active="currentStep === index"
        @click="goToStep(index)"
      />
    </div>
    
    <!-- Step content -->
    <component 
      :is="currentStepComponent" 
      v-model="configuration"
      @next="nextStep"
      @previous="previousStep"
    />
    
    <!-- Live preview -->
    <config-preview :config="configuration" />
  </div>
</template>
```

### 2. Real-time Build Monitoring
```vue
<template>
  <div class="build-monitor">
    <build-progress 
      :percentage="buildProgress" 
      :status="buildStatus"
      :logs="buildLogs"
    />
    
    <!-- Live log stream -->
    <log-viewer 
      :logs="buildLogs" 
      :auto-scroll="true"
      :follow="buildInProgress"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      buildLogs: [],
      buildProgress: 0,
      buildStatus: 'pending'
    };
  },
  mounted() {
    this.connectToLogStream();
  },
  methods: {
    connectToLogStream() {
      const ws = new WebSocket(`ws://localhost:8080/builds/${this.buildId}/logs`);
      ws.onmessage = (event) => {
        const logEntry = JSON.parse(event.data);
        this.buildLogs.push(logEntry);
        this.updateProgress(logEntry);
      };
    }
  }
};
</script>
```

## Resources and References

### Official Documentation
- [Vue.js Guide](https://vuejs.org/guide/) - Comprehensive Vue.js documentation
- [React Documentation](https://react.dev/) - Official React documentation
- [Angular Developer Guides](https://angular.io/docs) - Angular framework documentation
- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/) - Web Content Accessibility Guidelines

### Tools and Libraries
- [Vue CLI](https://cli.vuejs.org/) - Standard tooling for Vue.js development
- [Create React App](https://create-react-app.dev/) - Set up React projects quickly
- [Angular CLI](https://angular.io/cli) - Command line interface for Angular
- [axe-core](https://github.com/dequelabs/axe-core) - Accessibility testing engine

### Design Systems and UI Libraries
- [Vue Material](https://vuematerial.io/) - Material Design for Vue.js
- [Ant Design Vue](https://antdv.com/) - Enterprise-class UI design language
- [Material-UI](https://mui.com/) - React components implementing Material Design
- [Angular Material](https://material.angular.io/) - Material Design components for Angular

### Best Practices Articles
- [SPA Design Patterns](https://lembergsolutions.com/blog/design-approach-single-page-apps-tips-and-examples)
- [Dashboard Design Principles](https://www.uxpin.com/studio/blog/dashboard-design-principles/)
- [Progressive Enhancement Strategy](https://www.smashingmagazine.com/2009/04/progressive-enhancement-what-it-is-and-how-to-use-it/)
- [Form Accessibility Guide](https://webaim.org/techniques/formvalidation/)

---

**Note**: This guide focuses on modern web development practices specifically tailored for configuration management interfaces like PeiDocker. Always test thoroughly across different browsers, devices, and accessibility tools before deployment.
