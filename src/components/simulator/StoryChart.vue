<script setup lang="ts">
import dagre from '@dagrejs/dagre';
import {
  VueFlow, useVueFlow, ConnectionMode, ConnectionLineType,
  Position,
  type Node, type Edge,
} from '@vue-flow/core';
import { MiniMap } from '@vue-flow/minimap';
import {
  ref, onMounted, watch,
} from 'vue';

import '@vue-flow/core/dist/style.css';
import '@vue-flow/core/dist/theme-default.css';
import '@vue-flow/minimap/dist/style.css';

import {
  type GfChaptersInfo,
} from '../../types/assets';
import { CHAPTER_EDGES, CHAPTER_GROUPS } from './edges';
import StoryNode from './StoryNode.vue';

import jsonChapterPresets from '../../assets/chapters.json';

const chapterPresets: GfChaptersInfo = jsonChapterPresets;

const props = defineProps<{
  epName: string;
}>();
const emit = defineEmits<{
  'update:value': [value: string],
}>();

interface NodeData {
  label: string;
  type: 'circ' | 'square' | 'star';
  group?: number;
}
const nodes = ref<Node<NodeData>[]>([]);
const edges = ref<Edge[]>([]);
const {
  addEdges, updateNodeInternals,
  onConnect, onNodeClick, toObject,
} = useVueFlow();
onConnect((params) => {
  addEdges(params);
});

onNodeClick((event) => {
  emit('update:value', event.node.id);
});

function newGraph() {
  const graph = new dagre.graphlib.Graph<{
    id: string,
    label: string,
    group?: number,
  }>();
  graph.setDefaultEdgeLabel(() => ({}));
  graph.setGraph({ rankdir: 'LR' });
  return graph;
}

function layout(chapter: string) {
  const connectivity = newGraph();
  const stories = chapterPresets.main.find((c) => c.name.startsWith(`${chapter} `))?.stories;
  stories?.forEach((story) => {
    const id = typeof story.files[0] === 'string' ? story.files[0] : story.files[0][0];
    const label = story.name;
    connectivity.setNode(id, {
      id, label, width: 120, height: 8,
    });
  });
  const chapterEdges = CHAPTER_EDGES[chapter] ?? [];
  chapterEdges.forEach((edge) => connectivity.setEdge(edge.source, edge.target));
  let groupMinY: number[][] = [];
  if (CHAPTER_GROUPS[chapter]) {
    let paddingTop = 0;
    groupMinY = CHAPTER_GROUPS[chapter].map((group, i) => {
      const graph = newGraph();
      function copyDeep(id: string) {
        graph.setNode(id, connectivity.node(id));
        (connectivity.successors(id) as unknown as string[])?.forEach(copyDeep);
        connectivity.outEdges(id)?.forEach(({ v, w }) => {
          graph.setEdge(v, w);
        });
      }
      group.forEach(copyDeep);
      dagre.layout(graph);
      let maxX = 0;
      let maxY = 0;
      graph.nodes().forEach((id) => {
        const {
          x, y, width, height,
        } = graph.node(id);
        maxX = Math.max(maxX, x + width);
        maxY = Math.max(maxY, y + height);
        connectivity.setNode(id, {
          ...connectivity.node(id), x, y: y + paddingTop, group: i,
        });
      });
      const rect = [0, paddingTop, maxX, maxY + 20];
      paddingTop += maxY + 100;
      return rect;
    });
  } else {
    stories?.forEach((story, i) => {
      const id = typeof story.files[0] === 'string' ? story.files[0] : story.files[0][0];
      connectivity.setNode(id, {
        ...connectivity.node(id),
        x: (i % 5) * 180,
        y: Math.floor(i / 5) * 60,
      });
    });
  }
  return {
    nodes: connectivity.nodes().map((node): Node<NodeData> => {
      const {
        x, y, label, id,
      } = connectivity.node(node);
      const successors = connectivity.successors(node)?.length ?? 0;
      return {
        id,
        type: 'story',
        targetPosition: Position.Left,
        sourcePosition: Position.Right,
        position: { x, y },
        data: { label, type: successors >= 2 ? 'star' : 'square' },
      };
    }).concat(groupMinY.map(([x, y, w, h], i) => ({
      id: `group-${i}`,
      position: { x, y },
      width: w,
      height: h,
      focusable: false,
      selectable: false,
      draggable: false,
    }))),
    edges: chapterEdges,
  };
}

function updateChart(chapter: string) {
  const layoutResult = layout(chapter);
  nodes.value = layoutResult.nodes;
  if (layoutResult.edges.length === 0) {
    // eslint-disable-next-line no-alert
    alert(`本章节的选关界面还未录入……欢迎催更或是帮忙录入！
（帮忙录入的方法是连好线之后到浏览器 F12 控制台里输入 exportChart() 然后把输入发给我。）`);
  }
  edges.value = layoutResult.edges;
  const handle = setInterval(updateNodeInternals, 100);
  setTimeout(() => clearInterval(handle), 1000);
}

onMounted(() => {
  updateChart(props.epName);
});
watch(() => props.epName, (newEpName) => {
  updateChart(newEpName);
});

declare global {
  interface Window {
    exportChart: () => void;
  }
}

window.exportChart = () => {
  // eslint-disable-next-line no-console
  console.log(JSON.stringify(toObject().edges.map(({ source, target }) => ({ source, target }))));
};
</script>
<template>
  <div class="story-chart">
    <vue-flow :nodes="nodes" :edges="edges"
      :connection-mode="ConnectionMode.Strict"
      :connection-line-type="ConnectionLineType.SimpleBezier"
      :nodes-draggable="false"
      fit-view-on-init
    >
      <template #node-story="specialNodeProps">
        <story-node v-bind="specialNodeProps" />
      </template>
      <mini-map zoomable pannable />
    </vue-flow>
  </div>
</template>
<style scoped>
.story-chart {
  width: 100%;
  height: 70vh;

  --vf-node-bg: none;
  --vf-node-text: #fff;
}
.story-chart:deep(.vue-flow__node-default) {
  border: 3px solid white;
}
.story-chart:deep(.vue-flow__minimap) {
  background-color: #999;
  filter: invert(1);
}
.story-chart:deep(.vue-flow__node.selectable) {
  cursor: pointer;
}
.story-chart:deep(svg rect[id^="group-"]) {
  display: none;
}
</style>
