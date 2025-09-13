# Enhanced Graph Visualization System

A comprehensive React-based graph visualization system with interactive UI, what-if simulation, and real-time updates using Cytoscape.js.

## Features

### 🎯 Core Graph Visualization
- **Cytoscape.js Integration**: Professional graph rendering with dagre layout
- **Dynamic Node Styling**: Size by degree, color by sector/industry
- **Smart Edge Styling**: Color-coded by deal type, thickness by weight, dashed for predictions
- **Interactive Controls**: Zoom, pan, layout switching, export functionality

### 🔍 Interactive UI Components
- **Node Details Panel**: Comprehensive company information, connections, and metrics
- **What-If Simulation Panel**: Interactive scenario modeling with impact analysis
- **Citation Tooltips**: Evidence-based information with confidence scores
- **Real-time Status Indicators**: Connection status and live update toggles

### ⚡ Real-time Features
- **WebSocket Integration**: Live graph updates from backend
- **Prediction Toggle**: Show/hide AI-generated deal predictions
- **Auto-refresh**: Automatic data synchronization
- **Loading States**: Smooth user experience with proper feedback

### 🎮 What-If Simulation
- **Company Selection**: Dropdown menus with search functionality
- **Deal Configuration**: Type, value, and timeline sliders
- **Impact Analysis**: Affected nodes with path visualization
- **Confidence Scoring**: Reliability indicators for predictions

## File Structure

```
components/
├── GraphVisualization.tsx          # Core Cytoscape.js graph component
├── EnhancedGraphVisualization.tsx   # Main wrapper with all features
├── NodeDetailsPanel.tsx             # Side panel for node information
├── WhatIfSimulationPanel.tsx        # Simulation interface
└── CitationTooltip.tsx              # Evidence tooltips

services/
├── websocket.ts                     # Real-time WebSocket service
└── api.ts                          # Backend API integration

types/
└── index.ts                        # TypeScript definitions
```

## Dependencies

### Core Dependencies
```json
{
  "cytoscape": "^3.26.0",
  "cytoscape-dagre": "^2.5.0",
  "cytoscape-cose-bilkent": "^4.1.0",
  "react-hot-toast": "^2.4.1",
  "socket.io-client": "^4.7.2",
  "framer-motion": "^10.16.4",
  "react-select": "^5.8.0"
}
```

## Component Usage

### Basic Graph Visualization
```tsx
import { GraphVisualization } from '@/components/GraphVisualization'

<GraphVisualization
  data={graphData}
  onNodeClick={handleNodeClick}
  onEdgeClick={handleEdgeClick}
  showPredictions={showPredictions}
  selectedNode={selectedNode}
/>
```

### Enhanced Graph with All Features
```tsx
import { EnhancedGraphVisualization } from '@/components/EnhancedGraphVisualization'

<EnhancedGraphVisualization
  data={graphData}
  onDataUpdate={setGraphData}
  showPredictions={showPredictions}
  onTogglePredictions={handleTogglePredictions}
/>
```

### Node Details Panel
```tsx
import { NodeDetailsPanel } from '@/components/NodeDetailsPanel'

<NodeDetailsPanel
  nodeId={selectedNode}
  graphData={graphData}
  onClose={handleClose}
  showPredictions={showPredictions}
/>
```

### What-If Simulation
```tsx
import { WhatIfSimulationPanel } from '@/components/WhatIfSimulationPanel'

<WhatIfSimulationPanel
  graphData={graphData}
  onSimulationResult={handleSimulationResult}
/>
```

## Data Format

### Graph Data Structure
```typescript
interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  metadata: Record<string, any>
}

interface GraphNode {
  id: string
  label: string
  size: number
  color: string
  data: {
    sector?: string
    industry?: string
    market_cap?: number
    // ... other company data
  }
}

interface GraphEdge {
  id: string
  source: string
  target: string
  label: string
  weight: number
  color: string
  data: {
    deal_type: string
    deal_value?: number
    is_predicted?: boolean
    confidence_score?: number
    // ... other deal data
  }
}
```

## Styling System

### Sector Colors
```typescript
const SECTOR_COLORS = {
  'Technology': '#3B82F6',
  'Healthcare': '#10B981',
  'Finance': '#F59E0B',
  'Energy': '#EF4444',
  'Consumer': '#8B5CF6',
  'Industrial': '#6B7280',
  'Real Estate': '#EC4899',
  'Materials': '#84CC16',
  'Utilities': '#06B6D4',
  'Telecommunications': '#F97316'
}
```

### Deal Type Colors
- **Mergers/Acquisitions**: Red (#EF4444)
- **Partnerships**: Green (#10B981)
- **Investments**: Blue (#3B82F6)
- **IPOs**: Purple (#8B5CF6)
- **Predictions**: Orange (#F59E0B, dashed)

## WebSocket Events

### Incoming Events
- `graph_data_updated`: Full graph refresh
- `node_added`: New company added
- `node_removed`: Company removed
- `edge_added`: New deal added
- `edge_removed`: Deal removed
- `predictions_updated`: AI predictions updated
- `simulation_complete`: What-if simulation results

### Outgoing Events
- `join_room`: Subscribe to updates
- `request_graph_update`: Manual refresh
- `start_simulation`: Trigger what-if analysis
- `start_data_ingestion`: Begin data import

## Performance Optimizations

1. **Lazy Loading**: Components load data on demand
2. **Memoization**: React.memo and useCallback for expensive operations
3. **Virtual Scrolling**: Large lists in panels are virtualized
4. **Debounced Updates**: WebSocket events are batched
5. **Canvas Rendering**: Cytoscape.js uses hardware acceleration

## Accessibility Features

- **Keyboard Navigation**: Full keyboard support for all interactions
- **Screen Reader Support**: ARIA labels and descriptions
- **High Contrast Mode**: Configurable color schemes
- **Focus Management**: Proper focus handling for modals and panels

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## API Integration

The system integrates with backend endpoints for:
- Graph data retrieval (`/api/graph-data`)
- Company profiles (`/api/company/{id}`)
- What-if simulations (`/api/what-if`)
- Real-time updates (WebSocket connection)

## Development

### Running the Application
```bash
npm install
npm run dev
```

### Building for Production
```bash
npm run build
npm start
```

### Testing
```bash
npm test
```

## Troubleshooting

### Common Issues

1. **Graph Not Rendering**
   - Check if Cytoscape.js extensions are loaded
   - Verify data format matches expected structure
   - Ensure container has proper dimensions

2. **WebSocket Connection Failed**
   - Verify backend WebSocket server is running
   - Check network connectivity and firewall settings
   - Review WebSocket URL configuration

3. **Performance Issues**
   - Reduce number of nodes/edges for large graphs
   - Disable animations for better performance
   - Use simpler layout algorithms for complex graphs

### Debug Mode
Enable debug logging by setting:
```javascript
localStorage.setItem('debug', 'graph:*')
```

## Contributing

When adding new features:
1. Follow TypeScript strict mode
2. Add proper error handling
3. Include loading states
4. Write comprehensive tests
5. Update documentation

## License

This project is part of the dealflow analysis system and follows the main project license.
