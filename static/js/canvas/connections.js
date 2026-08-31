/**
 * DFD Architect — Data Flow SVG Connections & Arrow Routing
 */
const Connections = {
  // Returns closest connection port coordinates between two bounding boxes
  getPortPositions(srcNode, dstNode) {
    const srcW = srcNode.width || 160;
    const srcH = srcNode.height || 80;
    const dstW = dstNode.width || 160;
    const dstH = dstNode.height || 80;

    const srcCenter = { x: srcNode.pos_x + srcW / 2, y: srcNode.pos_y + srcH / 2 };
    const dstCenter = { x: dstNode.pos_x + dstW / 2, y: dstNode.pos_y + dstH / 2 };

    const dx = dstCenter.x - srcCenter.x;
    const dy = dstCenter.y - srcCenter.y;

    let srcPort, dstPort;

    if (Math.abs(dx) > Math.abs(dy)) {
      // Horizontal dominant
      if (dx > 0) {
        srcPort = { x: srcNode.pos_x + srcW, y: srcCenter.y, side: 'right' };
        dstPort = { x: dstNode.pos_x, y: dstCenter.y, side: 'left' };
      } else {
        srcPort = { x: srcNode.pos_x, y: srcCenter.y, side: 'left' };
        dstPort = { x: dstNode.pos_x + dstW, y: dstCenter.y, side: 'right' };
      }
    } else {
      // Vertical dominant
      if (dy > 0) {
        srcPort = { x: srcCenter.x, y: srcNode.pos_y + srcH, side: 'bottom' };
        dstPort = { x: dstCenter.x, y: dstNode.pos_y, side: 'top' };
      } else {
        srcPort = { x: srcCenter.x, y: srcNode.pos_y, side: 'top' };
        dstPort = { x: dstCenter.x, y: dstNode.pos_y + dstH, side: 'bottom' };
      }
    }

    return { srcPort, dstPort };
  },

  // Builds cubic Bezier curve path string
  calculateBezierPath(p1, p2) {
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;

    let cx1, cy1, cx2, cy2;

    if (p1.side === 'right' || p1.side === 'left') {
      const curveWeight = Math.max(40, Math.abs(dx) * 0.45);
      cx1 = p1.side === 'right' ? p1.x + curveWeight : p1.x - curveWeight;
      cy1 = p1.y;
      cx2 = p2.side === 'left' ? p2.x - curveWeight : p2.x + curveWeight;
      cy2 = p2.y;
    } else {
      const curveWeight = Math.max(40, Math.abs(dy) * 0.45);
      cx1 = p1.x;
      cy1 = p1.side === 'bottom' ? p1.y + curveWeight : p1.y - curveWeight;
      cx2 = p2.x;
      cy2 = p2.side === 'top' ? p2.y - curveWeight : p2.y + curveWeight;
    }

    return {
      path: `M ${p1.x} ${p1.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${p2.x} ${p2.y}`,
      midpoint: {
        x: (p1.x + p2.x) / 2,
        y: (p1.y + p2.y) / 2
      }
    };
  },

  renderFlows() {
    const svgGroup = document.getElementById('svg-flows-group');
    if (!svgGroup) return;
    svgGroup.innerHTML = '';

    const flows = State.getCurrentFlows();
    flows.forEach(flow => {
      const src = State.getComponentById(flow.source_id);
      const dst = State.getComponentById(flow.destination_id);
      if (!src || !dst) return;

      const { srcPort, dstPort } = this.getPortPositions(src, dst);
      const { path, midpoint } = this.calculateBezierPath(srcPort, dstPort);

      const isSelected = State.selectedFlowId === flow.id;
      const markerId = isSelected ? 'arrowhead-active' : 'arrowhead';

      // Flow Container Group
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('class', `dfd-flow-group ${isSelected ? 'selected' : ''}`);
      g.setAttribute('data-flow-id', flow.id);

      // Invisible thick stroke for easy clicking/hovering
      const ghostPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      ghostPath.setAttribute('d', path);
      ghostPath.setAttribute('class', 'dfd-flow-path-ghost');
      ghostPath.onclick = (e) => {
        e.stopPropagation();
        Designer.selectFlow(flow.id);
      };

      // Visible styled arrow path
      const visiblePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      visiblePath.setAttribute('d', path);
      visiblePath.setAttribute('class', `dfd-flow-path ${isSelected ? 'selected' : ''}`);
      visiblePath.setAttribute('marker-end', `url(#${markerId})`);
      if (flow.is_bidirectional) {
        visiblePath.setAttribute('marker-start', `url(#${markerId})`);
      }
      visiblePath.onclick = (e) => {
        e.stopPropagation();
        Designer.selectFlow(flow.id);
      };

      g.appendChild(ghostPath);
      g.appendChild(visiblePath);

      // Flow Label Pill
      const labelText = flow.flow_name || flow.flow_identifier || 'Data Flow';
      const labelWidth = Math.max(60, labelText.length * 7 + 16);
      const labelHeight = 22;

      const labelG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      labelG.setAttribute('class', 'dfd-flow-label');
      labelG.setAttribute('transform', `translate(${midpoint.x - labelWidth / 2}, ${midpoint.y - labelHeight / 2})`);
      labelG.onclick = (e) => {
        e.stopPropagation();
        Designer.selectFlow(flow.id);
      };

      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('class', 'dfd-flow-label-bg');
      rect.setAttribute('width', labelWidth);
      rect.setAttribute('height', labelHeight);

      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', labelWidth / 2);
      text.setAttribute('y', labelHeight / 2 + 3.5);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('fill', isSelected ? '#2563EB' : 'var(--text-primary)');
      text.setAttribute('font-size', '10.5px');
      text.textContent = labelText;

      labelG.appendChild(rect);
      labelG.appendChild(text);
      g.appendChild(labelG);

      svgGroup.appendChild(g);
    });
  },

  // Interactive Connection Drag Line Update
  updatePreviewLine(x1, y1, x2, y2) {
    const previewLine = document.getElementById('svg-preview-line');
    if (!previewLine) return;
    previewLine.setAttribute('d', `M ${x1} ${y1} L ${x2} ${y2}`);
    previewLine.style.display = 'block';
  },

  hidePreviewLine() {
    const previewLine = document.getElementById('svg-preview-line');
    if (previewLine) previewLine.style.display = 'none';
  }
};
