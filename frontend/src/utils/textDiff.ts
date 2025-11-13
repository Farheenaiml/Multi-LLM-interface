/**
 * Text Diff Utility
 * Implements a simple diff algorithm for comparing text content between panes
 */

export interface DiffSegment {
  type: 'added' | 'removed' | 'unchanged';
  text: string;
  startIndex: number;
  endIndex: number;
}

export interface DiffResult {
  segments: DiffSegment[];
  similarity: number; // 0-1 score indicating how similar the texts are
}

/**
 * Simple word-based diff algorithm
 * Compares two texts and returns segments showing differences
 */
export function computeTextDiff(text1: string, text2: string): DiffResult {
  // Handle empty strings
  if (!text1 && !text2) {
    return { segments: [], similarity: 1 };
  }
  
  if (!text1) {
    return {
      segments: [{
        type: 'added',
        text: text2,
        startIndex: 0,
        endIndex: text2.length
      }],
      similarity: 0
    };
  }
  
  if (!text2) {
    return {
      segments: [{
        type: 'removed',
        text: text1,
        startIndex: 0,
        endIndex: text1.length
      }],
      similarity: 0
    };
  }
  
  // Split texts into words for better granularity
  const words1 = text1.split(/(\s+)/).filter(word => word.length > 0);
  const words2 = text2.split(/(\s+)/).filter(word => word.length > 0);
  
  // Use Myers' diff algorithm (simplified)
  const segments = myersDiff(words1, words2);
  
  // Calculate similarity score
  const totalWords = Math.max(words1.length, words2.length);
  const unchangedWords = segments.filter(s => s.type === 'unchanged').length;
  const similarity = totalWords > 0 ? unchangedWords / totalWords : 1;
  
  return {
    segments,
    similarity
  };
}

/**
 * Simplified Myers' diff algorithm
 * More reliable than the previous LCS implementation
 */
function myersDiff(words1: string[], words2: string[]): DiffSegment[] {
  const segments: DiffSegment[] = [];
  let i = 0, j = 0, pos = 0;
  
  while (i < words1.length && j < words2.length) {
    if (words1[i] === words2[j]) {
      // Words match - unchanged
      segments.push({
        type: 'unchanged',
        text: words1[i],
        startIndex: pos,
        endIndex: pos + words1[i].length
      });
      pos += words1[i].length;
      i++;
      j++;
    } else {
      // Words don't match - look ahead to find next match
      let nextMatch1 = -1, nextMatch2 = -1;
      
      // Look for words2[j] in remaining words1
      for (let k = i + 1; k < Math.min(i + 10, words1.length); k++) {
        if (words1[k] === words2[j]) {
          nextMatch1 = k;
          break;
        }
      }
      
      // Look for words1[i] in remaining words2
      for (let k = j + 1; k < Math.min(j + 10, words2.length); k++) {
        if (words2[k] === words1[i]) {
          nextMatch2 = k;
          break;
        }
      }
      
      if (nextMatch1 !== -1 && (nextMatch2 === -1 || nextMatch1 - i <= nextMatch2 - j)) {
        // Remove words from words1 until match
        while (i < nextMatch1) {
          segments.push({
            type: 'removed',
            text: words1[i],
            startIndex: pos,
            endIndex: pos + words1[i].length
          });
          pos += words1[i].length;
          i++;
        }
      } else if (nextMatch2 !== -1) {
        // Add words from words2 until match
        while (j < nextMatch2) {
          segments.push({
            type: 'added',
            text: words2[j],
            startIndex: pos,
            endIndex: pos + words2[j].length
          });
          pos += words2[j].length;
          j++;
        }
      } else {
        // No match found nearby - treat as replacement
        segments.push({
          type: 'removed',
          text: words1[i],
          startIndex: pos,
          endIndex: pos + words1[i].length
        });
        pos += words1[i].length;
        i++;
        
        segments.push({
          type: 'added',
          text: words2[j],
          startIndex: pos,
          endIndex: pos + words2[j].length
        });
        pos += words2[j].length;
        j++;
      }
    }
  }
  
  // Add remaining words from words1 (removed)
  while (i < words1.length) {
    segments.push({
      type: 'removed',
      text: words1[i],
      startIndex: pos,
      endIndex: pos + words1[i].length
    });
    pos += words1[i].length;
    i++;
  }
  
  // Add remaining words from words2 (added)
  while (j < words2.length) {
    segments.push({
      type: 'added',
      text: words2[j],
      startIndex: pos,
      endIndex: pos + words2[j].length
    });
    pos += words2[j].length;
    j++;
  }
  
  return segments;
}

/**
 * Clean up response tags and formatting artifacts from content
 */
function cleanResponseTags(content: string): string {
  return content
    // Remove [Response N] tags
    .replace(/\[Response \d+\]/g, '')
    // Remove [User] and [Assistant] tags at the start of lines
    .replace(/^\[(?:User|Assistant)\]\s*/gm, '')
    // Clean up multiple newlines
    .replace(/\n{3,}/g, '\n\n')
    // Trim whitespace
    .trim();
}

/**
 * Utility to get content from a pane for comparison
 * @param pane - The pane to extract content from
 * @param mode - What content to extract: 'latest' | 'all-assistant' | 'full-conversation'
 */
export function getPaneContentForComparison(pane: any, mode: 'latest' | 'all-assistant' | 'full-conversation' = 'latest'): string {
  // Debug logging to check what mode is being used
  console.log('getPaneContentForComparison called with mode:', mode, 'for pane:', pane?.id);
  
  if (!pane || !pane.messages || pane.messages.length === 0) {
    console.log('getPaneContentForComparison: No pane or messages');
    return '';
  }
  
  let content = '';
  
  switch (mode) {
    case 'latest': {
      // Get only the last assistant message
      const assistantMessages = pane.messages.filter((msg: any) => msg.role === 'assistant');
      if (assistantMessages.length === 0) {
        console.log('getPaneContentForComparison: No assistant messages found');
        return '';
      }
      const lastMessage = assistantMessages[assistantMessages.length - 1];
      content = lastMessage.content || '';
      break;
    }
    
    case 'all-assistant': {
      // Get all assistant messages concatenated without tags
      const assistantMessages = pane.messages.filter((msg: any) => msg.role === 'assistant');
      if (assistantMessages.length === 0) {
        console.log('getPaneContentForComparison: No assistant messages found');
        return '';
      }
      content = assistantMessages
        .map((msg: any) => msg.content || '')
        .filter((content: string) => content.trim().length > 0) // Remove empty messages
        .join('\n\n---\n\n'); // Use a cleaner separator
      break;
    }
    
    case 'full-conversation': {
      // Get the entire conversation with cleaner formatting
      content = pane.messages
        .filter((msg: any) => msg.content && msg.content.trim().length > 0)
        .map((msg: any) => {
          const role = msg.role === 'user' ? 'User' : 'Assistant';
          return `${role}: ${msg.content}`;
        })
        .join('\n\n');
      break;
    }
    
    default:
      content = '';
  }
  
  // Clean up any existing response tags that might be in the content
  content = cleanResponseTags(content);
  
  console.log('getPaneContentForComparison: Returning content length:', content.length, 'for mode:', mode);
  return content;
}

/**
 * Utility to format diff segments for display
 */
export function formatDiffSegments(segments: DiffSegment[]): string {
  return segments.map(segment => {
    switch (segment.type) {
      case 'added':
        return `<span class="diff-added">${escapeHtml(segment.text)}</span>`;
      case 'removed':
        return `<span class="diff-removed">${escapeHtml(segment.text)}</span>`;
      case 'unchanged':
        return `<span class="diff-unchanged">${escapeHtml(segment.text)}</span>`;
      default:
        return escapeHtml(segment.text);
    }
  }).join('');
}

/**
 * Simple HTML escape utility
 */
function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}