import { useEffect, useRef } from 'react';

/**
 * Custom React hook that uses IntersectionObserver to add 'is-visible' class
 * to the referenced DOM element when it enters the viewport.
 *
 * @param {Object} options - Optional configuration for IntersectionObserver
 * @param {number|number[]} [options.threshold=0.1] - Percentage of target visibility to trigger observer
 * @param {string} [options.rootMargin='0px'] - Margin around the root element
 * @param {boolean} [options.triggerOnce=true] - If true, unobserves after adding 'is-visible'
 * @returns {React.RefObject} Ref to attach to the target DOM element
 */
export const useScrollAnimation = (options = {}) => {
  const { threshold = 0.1, rootMargin = '0px', triggerOnce = true } = options;
  const elementRef = useRef(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            element.classList.add('is-visible');
            if (triggerOnce) {
              observer.unobserve(element);
            }
          } else if (!triggerOnce) {
            element.classList.remove('is-visible');
          }
        });
      },
      { threshold, rootMargin }
    );

    observer.observe(element);

    return () => {
      if (element) {
        observer.unobserve(element);
      }
    };
  }, [threshold, rootMargin, triggerOnce]);

  return elementRef;
};

export default useScrollAnimation;
