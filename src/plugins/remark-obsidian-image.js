import { visit } from 'unist-util-visit';

export default function remarkObsidianImage({ base = '' } = {}) {
  return (tree) => {
    visit(tree, 'text', (node, index, parent) => {
      const regex = /!\[\[([^\]]+)\]\]/g;
      let match;
      const newNodes = [];
      let lastIndex = 0;

      while ((match = regex.exec(node.value)) !== null) {
        if (match.index > lastIndex) {
          newNodes.push({ type: 'text', value: node.value.slice(lastIndex, match.index) });
        }
        const filename = match[1];
        newNodes.push({
          type: 'image',
          url: `${base}/images/${filename}`,
          alt: filename,
          title: null,
        });
        lastIndex = match.index + match[0].length;
      }

      if (newNodes.length > 0) {
        if (lastIndex < node.value.length) {
          newNodes.push({ type: 'text', value: node.value.slice(lastIndex) });
        }
        parent.children.splice(index, 1, ...newNodes);
        return index + newNodes.length;
      }
    });
  };
}
