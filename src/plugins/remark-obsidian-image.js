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
        const [rawFilename, rawCaption] = match[1].split('|');
        const filename = rawFilename.trim();
        const caption  = rawCaption?.trim();
        const src      = `${base}/images/${filename}`;

        if (caption) {
          newNodes.push({
            type: 'html',
            value: `<figure><img src="${src}" alt="${caption}" /><figcaption>${caption}</figcaption></figure>`,
          });
        } else {
          newNodes.push({
            type: 'image',
            url: src,
            alt: filename,
            title: null,
          });
        }
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
