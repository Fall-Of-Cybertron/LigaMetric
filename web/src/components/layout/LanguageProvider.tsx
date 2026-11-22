'use client';

import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { translateText, type Locale } from '@/lib/i18n';

interface LanguageContextValue {
  lang: Locale;
  setLang: (next: Locale) => void;
  t: (text: string) => string;
}

const LanguageContext = createContext<LanguageContextValue>({
  lang: 'tr',
  setLang: () => undefined,
  t: (text: string) => text,
});

const STORAGE_KEY = 'siperlig_lang';
const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'CODE', 'PRE']);
const TRANSLATABLE_ATTRS = ['placeholder', 'title', 'aria-label'] as const;

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Locale>('tr');
  const langRef = useRef<Locale>('tr');
  const originalTextMap = useRef(new WeakMap<Text, string>());
  const lastAppliedTextMap = useRef(new WeakMap<Text, string>());
  const originalAttrMap = useRef(new WeakMap<Element, Record<string, string>>());
  const isApplyingRef = useRef(false);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(STORAGE_KEY) as Locale | null;
      if (saved === 'tr' || saved === 'en' || saved === 'de') {
        langRef.current = saved;
        setLangState(saved);
      }
    } catch {
      // Ignore storage access errors in restricted environments
    }
  }, []);

  const setLang = useCallback((next: Locale) => {
    langRef.current = next;
    setLangState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Ignore storage write errors
    }
  }, []);

  useEffect(() => {
    langRef.current = lang;
    document.documentElement.lang = lang;
    document.title =
      lang === 'en'
        ? 'Süper Lig Statistics & Analytics Center'
        : lang === 'de'
          ? 'Süper Lig Statistik- & Analysezentrum'
          : 'Süper Lig İstatistik & Analiz Merkezi';

    const shouldSkipElement = (el: Element | null): boolean => {
      let cur: Element | null = el;
      while (cur) {
        if (SKIP_TAGS.has(cur.tagName) || cur.hasAttribute('data-no-i18n')) {
          return true;
        }
        cur = cur.parentElement;
      }
      return false;
    };

    const processTextNode = (node: Text, targetLang: Locale) => {
      if (shouldSkipElement(node.parentElement)) return;
      const curVal = node.nodeValue ?? '';
      if (!curVal.trim()) return;

      const lastApplied = lastAppliedTextMap.current.get(node);
      if (lastApplied !== curVal || !originalTextMap.current.has(node)) {
        originalTextMap.current.set(node, curVal);
      }
      const sourceTr = originalTextMap.current.get(node) ?? curVal;
      const nextVal = targetLang === 'tr' ? sourceTr : translateText(sourceTr, targetLang);
      if (node.nodeValue !== nextVal) {
        node.nodeValue = nextVal;
      }
      lastAppliedTextMap.current.set(node, nextVal);
    };

    const processAttributes = (el: Element, targetLang: Locale) => {
      if (shouldSkipElement(el)) return;
      let stored = originalAttrMap.current.get(el);
      for (const attr of TRANSLATABLE_ATTRS) {
        if (!el.hasAttribute(attr)) continue;
        const curAttrVal = el.getAttribute(attr) ?? '';
        if (!stored) {
          stored = {};
          originalAttrMap.current.set(el, stored);
        }
        if (!(attr in stored)) {
          stored[attr] = curAttrVal;
        }
        const sourceTr = stored[attr];
        const nextAttrVal = targetLang === 'tr' ? sourceTr : translateText(sourceTr, targetLang);
        if (curAttrVal !== nextAttrVal) {
          el.setAttribute(attr, nextAttrVal);
        }
      }
    };

    const applyTreeTranslation = (root: Node, targetLang: Locale) => {
      if (root.nodeType === Node.TEXT_NODE) {
        processTextNode(root as Text, targetLang);
        return;
      }
      if (root.nodeType === Node.ELEMENT_NODE) {
        processAttributes(root as Element, targetLang);
      }

      const walker = document.createTreeWalker(
        root,
        NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT
      );
      let current: Node | null = walker.currentNode;
      while (current) {
        if (current.nodeType === Node.TEXT_NODE) {
          processTextNode(current as Text, targetLang);
        } else if (current.nodeType === Node.ELEMENT_NODE) {
          processAttributes(current as Element, targetLang);
        }
        current = walker.nextNode();
      }
    };

    const runSync = (root: Node) => {
      if (isApplyingRef.current) return;
      isApplyingRef.current = true;
      try {
        applyTreeTranslation(root, langRef.current);
      } finally {
        isApplyingRef.current = false;
      }
    };

    runSync(document.body);

    const observer = new MutationObserver((mutations) => {
      if (isApplyingRef.current) return;
      isApplyingRef.current = true;
      try {
        const currentLang = langRef.current;
        for (const mut of mutations) {
          if (mut.type === 'characterData' && mut.target.nodeType === Node.TEXT_NODE) {
            processTextNode(mut.target as Text, currentLang);
          } else if (mut.type === 'childList') {
            mut.addedNodes.forEach((added) => {
              applyTreeTranslation(added, currentLang);
            });
          } else if (mut.type === 'attributes' && mut.target.nodeType === Node.ELEMENT_NODE) {
            const el = mut.target as Element;
            const attrName = mut.attributeName;
            if (attrName && (TRANSLATABLE_ATTRS as readonly string[]).includes(attrName)) {
              const curVal = el.getAttribute(attrName) ?? '';
              const stored = originalAttrMap.current.get(el) ?? {};
              const expected =
                currentLang === 'tr'
                  ? stored[attrName]
                  : stored[attrName]
                    ? translateText(stored[attrName], currentLang)
                    : undefined;
              if (expected !== curVal) {
                stored[attrName] = curVal;
                originalAttrMap.current.set(el, stored);
              }
              processAttributes(el, currentLang);
            }
          }
        }
      } finally {
        observer.takeRecords();
        isApplyingRef.current = false;
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ['placeholder', 'title', 'aria-label'],
    });

    return () => {
      observer.disconnect();
    };
  }, [lang]);

  const t = useCallback((text: string) => translateText(text, lang), [lang]);

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>{children}</LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextValue {
  return useContext(LanguageContext);
}
