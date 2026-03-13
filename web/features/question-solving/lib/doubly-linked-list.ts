/**
 * Doubly-linked list implementation for pagination cache
 * 
 * This class manages a sliding window of cached pages using a doubly-linked
 * list structure. It ensures only a maximum number of pages are kept in
 * memory at any time, with intelligent eviction based on distance from
 * current position.
 */

import { CacheNode } from "../types/pagination-cache.types";
import { HybridProblem } from "@/shared/stores/problems/cache";

export class DoublyLinkedList {
  private head: CacheNode | null = null;
  private tail: CacheNode | null = null;
  private nodeMap: Map<number, CacheNode> = new Map();
  private currentNode: CacheNode | null = null;
  private maxSize: number;
  private sectionId: string;

  constructor(sectionId: string, maxSize: number = 3) {
    this.sectionId = sectionId;
    this.maxSize = maxSize;
  }

  /**
   * Create a new cache node
   */
  private createNode(
    pageNumber: number,
    questionData: HybridProblem[]
  ): CacheNode {
    const now = Date.now();
    return {
      pageNumber,
      sectionId: this.sectionId,
      questionData,
      next: null,
      previous: null,
      createdAt: now,
      lastAccessed: now,
    };
  }

  /**
   * Add a new page to the cache
   * Handles insertion at appropriate position and eviction if needed
   */
  addPage(pageNumber: number, questionData: HybridProblem[]): CacheNode {
    console.log(`🔗 Adding page ${pageNumber} to cache (section: ${this.sectionId})`);

    // If page already exists, update it
    if (this.nodeMap.has(pageNumber)) {
      const existingNode = this.nodeMap.get(pageNumber)!;
      existingNode.questionData = questionData;
      existingNode.lastAccessed = Date.now();
      return existingNode;
    }

    const newNode = this.createNode(pageNumber, questionData);
    this.nodeMap.set(pageNumber, newNode);

    // If this is the first node
    if (!this.head) {
      this.head = this.tail = newNode;
      this.currentNode = newNode;
      return newNode;
    }

    // Find the correct position to insert (maintain sorted order)
    this.insertNodeInOrder(newNode);

    // Check if we need to evict nodes
    if (this.nodeMap.size > this.maxSize) {
      this.evictLRU();
    }

    return newNode;
  }

  /**
   * Insert node in correct position to maintain page number order
   */
  private insertNodeInOrder(newNode: CacheNode): void {
    let current = this.head;

    // Find insertion point
    while (current && current.pageNumber < newNode.pageNumber) {
      current = current.next;
    }

    if (!current) {
      // Insert at end
      if (this.tail) {
        this.tail.next = newNode;
        newNode.previous = this.tail;
        this.tail = newNode;
      }
    } else if (!current.previous) {
      // Insert at beginning
      newNode.next = this.head;
      if (this.head) {
        this.head.previous = newNode;
      }
      this.head = newNode;
    } else {
      // Insert in middle
      newNode.previous = current.previous;
      newNode.next = current;
      current.previous.next = newNode;
      current.previous = newNode;
    }
  }

  /**
   * Get a page from the cache
   */
  getPage(pageNumber: number): CacheNode | null {
    const node = this.nodeMap.get(pageNumber);
    if (node) {
      node.lastAccessed = Date.now();
      console.log(`✅ Cache hit for page ${pageNumber} (section: ${this.sectionId})`);
      return node;
    }
    console.log(`❌ Cache miss for page ${pageNumber} (section: ${this.sectionId})`);
    return null;
  }

  /**
   * Set the current active page
   */
  setCurrentPage(pageNumber: number): CacheNode | null {
    const node = this.nodeMap.get(pageNumber);
    if (node) {
      this.currentNode = node;
      node.lastAccessed = Date.now();
      return node;
    }
    return null;
  }

  /**
   * Get the current active page
   */
  getCurrentPage(): CacheNode | null {
    return this.currentNode;
  }

  /**
   * Navigate to next page if it exists in cache
   */
  getNextPage(): CacheNode | null {
    if (!this.currentNode) return null;

    const nextNode = this.currentNode.next;
    if (nextNode) {
      this.currentNode = nextNode;
      nextNode.lastAccessed = Date.now();
      return nextNode;
    }
    return null;
  }

  /**
   * Navigate to previous page if it exists in cache
   */
  getPreviousPage(): CacheNode | null {
    if (!this.currentNode) return null;

    const prevNode = this.currentNode.previous;
    if (prevNode) {
      this.currentNode = prevNode;
      prevNode.lastAccessed = Date.now();
      return prevNode;
    }
    return null;
  }

  /**
   * Evict the node that is furthest from current position
   */
  private evictLRU(): void {
    if (!this.currentNode || this.nodeMap.size <= this.maxSize) return;

    let nodeToEvict: CacheNode | null = null;
    let maxDistance = -1;

    // Find the node with maximum distance from current page
    for (const pageNumber of Array.from(this.nodeMap.keys())) {
      const node = this.nodeMap.get(pageNumber)!;
      const distance = Math.abs(pageNumber - this.currentNode.pageNumber);
      if (distance > maxDistance) {
        maxDistance = distance;
        nodeToEvict = node;
      }
    }

    if (nodeToEvict) {
      console.log(`🗑️  Evicting page ${nodeToEvict.pageNumber} (distance: ${maxDistance}) from cache`);
      this.removeNode(nodeToEvict);
    }
  }

  /**
   * Remove a specific node from the list
   */
  private removeNode(node: CacheNode): void {
    // Remove from map
    this.nodeMap.delete(node.pageNumber);

    // Update links
    if (node.previous) {
      node.previous.next = node.next;
    } else {
      this.head = node.next;
    }

    if (node.next) {
      node.next.previous = node.previous;
    } else {
      this.tail = node.previous;
    }

    // Update current node if we're removing it
    if (this.currentNode === node) {
      this.currentNode = node.next || node.previous;
    }
  }

  /**
   * Check if a page exists in cache
   */
  hasPage(pageNumber: number): boolean {
    return this.nodeMap.has(pageNumber);
  }

  /**
   * Get all cached page numbers
   */
  getCachedPageNumbers(): number[] {
    return Array.from(this.nodeMap.keys()).sort((a, b) => a - b);
  }

  /**
   * Get cache statistics
   */
  getStats(): {
    size: number;
    maxSize: number;
    currentPage: number | null;
    cachedPages: number[];
    memoryEstimate: number;
  } {
    const cachedPages = this.getCachedPageNumbers();

    // Rough memory estimate (each question ~1KB)
    let totalQuestions = 0;
    for (const node of Array.from(this.nodeMap.values())) {
      totalQuestions += node.questionData.length;
    }

    return {
      size: this.nodeMap.size,
      maxSize: this.maxSize,
      currentPage: this.currentNode?.pageNumber || null,
      cachedPages,
      memoryEstimate: totalQuestions * 1024, // 1KB per question estimate
    };
  }

  /**
   * Clear all nodes from cache
   */
  clear(): void {
    console.log(`🧹 Clearing cache for section: ${this.sectionId}`);
    this.head = null;
    this.tail = null;
    this.currentNode = null;
    this.nodeMap.clear();
  }

  /**
   * Get the range of pages that should be prefetched
   * Returns page numbers that should be loaded in background
   */
  getPrefetchTargets(direction: 'next' | 'previous' | 'both' = 'both'): number[] {
    if (!this.currentNode) return [];

    const targets: number[] = [];
    const currentPage = this.currentNode.pageNumber;

    if (direction === 'next' || direction === 'both') {
      // Check if next page needs prefetching
      if (!this.hasPage(currentPage + 1)) {
        targets.push(currentPage + 1);
      }
    }

    if (direction === 'previous' || direction === 'both') {
      // Check if previous page needs prefetching
      if (currentPage > 1 && !this.hasPage(currentPage - 1)) {
        targets.push(currentPage - 1);
      }
    }

    return targets;
  }

  /**
   * Debug method to visualize the current state of the list
   */
  debugPrint(): void {
    console.log(`\n🔗 DoublyLinkedList State (${this.sectionId}):`);
    console.log(`   Size: ${this.nodeMap.size}/${this.maxSize}`);
    console.log(`   Current: ${this.currentNode?.pageNumber || 'null'}`);

    let current = this.head;
    const nodes: string[] = [];
    while (current) {
      const marker = current === this.currentNode ? ' [CURRENT]' : '';
      nodes.push(`${current.pageNumber}${marker}`);
      current = current.next;
    }
    console.log(`   Order: ${nodes.join(' <-> ')}`);
    console.log('');
  }
}